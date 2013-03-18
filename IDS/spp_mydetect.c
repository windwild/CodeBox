/*
 * spp_mydetect.c
 */

#include <sys/types.h>
#include <stdlib.h>
#include <ctype.h>
#include <rpc/types.h>

/*
 * If you're going to issue any alerts from this preproc you 
 * should include generators.h and event_wrapper.h
 */
#include "generators.h"
#include "event_wrapper.h"

#include "util.h"
#include "plugbase.h"
#include "parser.h"

#include <netinet/ether.h>
#include <sfutil/sflsq.h>
#include <sfutil/sfghash.h>
#include <netinet/ip.h>
#include <arpa/inet.h>
#include <netinet/tcp.h>

/*
 * put in other inculdes as necessary
 */

/* 
 * your preprocessor header file goes here if necessary, don't forget
 * to include the header file in plugbase.h too!
 */
#include "spp_mydetect.h"

/*
 * Global variables - for our own state-tracking. -pclee
 */
unsigned int myPacketCount;
struct{
    unsigned int t_ip;
    unsigned int t_port;
    int syn_th;
    int hh_th;
    double syn_win;
    double hh_win;
    unsigned int payload;
} myConfig;

struct hhstruct{
    int payload;
    SF_QUEUE *list;
    int hh_switch;
};

struct myinfo{
    unsigned int src_ip;
    unsigned int dst_ip;
    int src_port;
    int dst_port;
    double timestamp;
    unsigned int payload;
};

SF_LIST *synlist;
SFGHASH *synhash;
SFGHASH *hhhash;
int syn_switch;
FILE *log_file;

/* 
 * function prototypes go here
 */

static void MyDetectInit(char *);
static void ParseMyDetectArgs(char *);
static void PreprocFunction(Packet *, void*);
static void PreprocCleanExitFunction(int, void *);
static void PreprocRestartFunction(int, void *);

/*
 * Function: SetupMyDetect()
 *
 * Purpose: Registers the preprocessor keyword and initialization 
 *          function into the preprocessor list.  This is the function that
 *          gets called from InitPreprocessors() in plugbase.c.
 *
 * Arguments: None.
 *
 * Returns: void function
 *
 */
void SetupMyDetect()
{
    /* 
     * link the preprocessor keyword to the init function in 
     * the preproc list 
     */
    RegisterPreprocessor("mydetect", MyDetectInit);

    printf("Preprocessor: MyDetect is setup...\n");
}


/*
 * Function: MyDetectInit(u_char *)
 *
 * Purpose: Calls the argument parsing function, performs final setup on data
 *          structs, links the preproc function into the function list.
 *
 * Arguments: args => ptr to argument string
 *
 * Returns: void function
 *
 */
static void MyDetectInit(char *args)
{
    printf("Preprocessor: MyDetect Initialized\n");

    /* 
     * parse the argument list from the rules file 
     */
    ParseMyDetectArgs(args);

    /* 
     * perform any other initialization functions that are required here
     */
	myPacketCount = 0;

    /* 
     * Set the preprocessor function into the function list.
	 * AddFuncToPreprocList() takes additional priority parameters. 
	 * I just pick the ones that work for our purpose. -pclee
     */
    AddFuncToPreprocList(PreprocFunction, PRIORITY_LAST, 0, PROTO_BIT__ALL);
	AddFuncToCleanExitList(PreprocCleanExitFunction, NULL);
	AddFuncToRestartList(PreprocRestartFunction, NULL);
}



/*
 * Function: ParseMyDetectArgs(char *)
 *
 * Purpose: Process the preprocessor arguements from the rules file and 
 *          initialize the preprocessor's data struct.  This function doesn't
 *          have to exist if it makes sense to parse the args in the init 
 *          function.
 *
 * Arguments: args => argument list
 *
 * Returns: void function
 *
 */
static void ParseMyDetectArgs(char *args)
{
    char **toks;
    int num_toks;
    int i;
    toks = mSplit(args, " ", 0, &num_toks, '\\');
    if (num_toks != 12){
        ParseError("Invalid arguments to MyDectect.");
    }
    // printf("IP :%s\n",toks[1]);
    myConfig.t_ip = inet_addr(toks[1]);
    myConfig.t_port = atoi(toks[3]);
    myConfig.syn_th = atoi(toks[5]);
    myConfig.hh_th = atoi(toks[7]);
    myConfig.syn_win = atof(toks[9]);
    myConfig.hh_win = atof(toks[11]);
    
    // printf("syn_win: %u\n",myConfig.t_ip);
    synlist = sflist_new();
    synhash = sfghash_new(13, 0, 0, free);
    hhhash = sfghash_new(13, 0, 0, free);
    log_file = fopen("detect_log.dat","w");
    syn_switch = 1;
}


/*
 * Function: PreprocFunction(Packet *, void* )
 *
 * Purpose: Perform the preprocessor's intended function.  This can be
 *          simple (statistics collection) or complex (IP defragmentation)
 *          as you like.  Try not to destroy the performance of the whole
 *          system by trying to do too much....
 *
 * Arguments: p => pointer to the current packet data struct 
 *
 * Returns: void function
 *
 */
static void PreprocFunction(Packet *p, void* context)
{

    /* your preproc function goes here.... */

    /* 
     * if you need to issue an alert from your preprocessor, check out 
     * event_wrapper.h, there are some useful helper functions there
     */
	myPacketCount++;
    struct ether_header* eth_hdr;
    struct ip *ip_hdr;
    unsigned int src_ip, dst_ip;
    int src_port, dst_port;
    
	eth_hdr = (struct ether_header*)(p->pkt);
    if (ntohs(eth_hdr->ether_type) != ETH_P_IP){
        return ;
    }
    
	ip_hdr = (struct ip*)(p->pkt +14);
	
    
    // if (ntohs(ip_hdr->ip_p) != IPPROTO_TCP){
    //     printf("Drop NON-TCP packet\n");
    //     return ;
    // }
    
    struct myinfo* info = (struct myinfo*)malloc(sizeof(struct myinfo));
    info->src_ip = ip_hdr->ip_src.s_addr;
    info->dst_ip = ip_hdr->ip_dst.s_addr;
    info->src_port = ntohs(p->tcph->th_sport);
    info->dst_port = ntohs(p->tcph->th_dport);
    info->timestamp = (double)p->pkth->ts.tv_usec / 1000000 + p->pkth->ts.tv_sec;
    info->payload = ntohs(ip_hdr->ip_len) - (ip_hdr->ip_hl << 2);
    
    struct myinfo *info_temp, *pop_item;
    int temp;
    if( syn_switch && (p->tcph->th_flags & TH_SYN) && (info->dst_ip == myConfig.t_ip) && (info->dst_port == myConfig.t_port) ){
        if( (info_temp = sfghash_find(synhash,&(info->src_ip))) == NULL ){
            if(sfghash_add(synhash, &(info->src_ip), (void *)info) != SFGHASH_OK){
                FatalError("cannot add to synhash");
            }
            sflist_add_tail(synlist,(NODE_DATA)info);
            if(sflist_count(synlist) > myConfig.syn_th){
                pop_item = (struct myinfo*)sflist_first(synlist);
                while(sflist_count(synlist) > 0 && pop_item->timestamp < info->timestamp - myConfig.syn_win ){
                    sflist_remove_head(synlist);
                    pop_item = (struct myinfo*)sflist_first(synlist);
                }
                if(sflist_count(synlist) > myConfig.syn_th && info->timestamp - pop_item->timestamp < myConfig.syn_win){
                    printf("SYN attack detected!!!@%d \n", myPacketCount);
                    syn_switch = 0;
                    fprintf(log_file, "SYN attack: %d:%d@%f\n",pop_item->src_ip,pop_item->src_port,pop_item->timestamp);
                    while(sflist_count(synlist) > 0){
                        pop_item = (struct myinfo*)sflist_remove_head(synlist);
                        fprintf(log_file, "SYN attack: %d:%d@%f\n",pop_item->src_ip,pop_item->src_port,pop_item->timestamp);
                    }
                }
            }
        }
    }
    
    struct hhstruct *hh;
    SF_LIST *hhlist;
    if( (hh = sfghash_find(hhhash,&(info->src_ip))) == NULL ){
        hhlist = sflist_new();
        sflist_add_tail(hhlist, info);
        hh = (struct hhstruct*)malloc(sizeof(struct hhstruct));
        hh->payload = info->payload;
        hh->list = hhlist;
        hh->hh_switch = 1;
        sfghash_add(hhhash, &info->src_ip, hh);
    }else if(hh->hh_switch){
        hh->payload += info->payload;
        sflist_add_tail(hh->list, info);
        if(hh->payload > myConfig.hh_th && sfghash_count(hh->list) > 0){
            pop_item = (struct myinfo*)sflist_first(hh->list);
            while(pop_item->timestamp < info->timestamp - myConfig.hh_win ){
                (struct myinfo*)sflist_remove_head(hh->list);
                pop_item = (struct myinfo*)sflist_first(hh->list);
                hh->payload -= pop_item->payload;
            }
            if(info->timestamp - pop_item->timestamp < myConfig.hh_win){
                printf("HH attack detected!!!@%d \n", myPacketCount);
                fprintf(log_file, "Heavy Hitter attack: %d,%u\n", pop_item->src_ip, hh->payload);
                hh->hh_switch = 0;
            }
        }
    }
    
    
    // manually stop
    if(myPacketCount > 80){
        FatalError("over 80 packets");
    }
}


/* 
 * Function: PreprocCleanExitFunction(int, void *)
 *
 * Purpose: This function gets called when Snort is exiting, if there's
 *          any cleanup that needs to be performed (e.g. closing files)
 *          it should be done here.
 *
 * Arguments: signal => the code of the signal that was issued to Snort
 *            data => any arguments or data structs linked to this 
 *                    functioin when it was registered, may be
 *                    needed to properly exit
 *       
 * Returns: void function
 */                   
static void PreprocCleanExitFunction(int signal, void *data)
{
	/* clean exit code goes here */
	printf("myPacketCount = %u\n", myPacketCount);
    fclose(log_file);
}


/* 
 * Function: PreprocRestartFunction(int, void *)
 *
 * Purpose: This function gets called when Snort is restarting on a SIGHUP,
 *          if there's any initialization or cleanup that needs to happen
 *          it should be done here.
 *
 * Arguments: signal => the code of the signal that was issued to Snort
 *            data => any arguments or data structs linked to this 
 *                    functioin when it was registered, may be
 *                    needed to properly exit
 *       
 * Returns: void function
 */                   
static void PreprocRestartFunction(int signal, void *foo)
{
       /* restart code goes here */
}
