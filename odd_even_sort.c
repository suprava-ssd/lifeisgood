#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>

int main(int argc, char *argv[]) {
    int i;
    pid_t pid;
    int status;
    if (argc < 2) {
        printf("Provide the inputs as this: %s num1 num2 num3 ... When you are done, press ENTER.\n", argv[0]);
        return 1;
    }
    
    int n = argc - 1;
    
    int *numbers = (int*)malloc(n * sizeof(int));
    char **args = (char**)malloc((n + 2) * sizeof(char*));
    
    for (i = 0; i < n; i++) {
        numbers[i] = atoi(argv[i+1]);
    }
    
    for (i = 0; i < n; i++) {
        args[i+1] = (char*)malloc(20 * sizeof(char));
        sprintf(args[i+1], "%d", numbers[i]);
    }
    args[n+1] = NULL;
    
    pid = fork();
    
    if (pid < 0) {

        perror("Error in Fork. Fork could not be called!");
        return 1;
    } 
    else if (pid == 0) {

        args[0] = "./sort";
        execv("./sort", args);
        
        perror("The program could not execute sort.c");
        exit(1);
    } 
    else {

        waitpid(pid, &status, 0);

        pid = fork();
        
        if (pid < 0) {
            perror("Error in Fork. Fork could not be called!");
            return 1;
        } 
        else if (pid == 0) {
            args[0] = "./oddeven";
            execv("./oddeven", args);
            
            perror("The program could not execute oddeven.c");
            exit(1);
        } 
        else {

            waitpid(pid, &status, 0);
            
            for (i = 1; i <= n; i++) {
                free(args[i]);
            }
            free(args);
            free(numbers);
        }
    }
    
    return 0;
}
