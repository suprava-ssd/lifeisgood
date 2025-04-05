#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <sys/types.h>
#include <sys/wait.h>

#define MAX_NUMBERS 100
#define MAX_LINE_LENGTH 1024

int main() {
    int count;
    int numbers[MAX_NUMBERS];

    // Get user input
    printf("Enter the number of elements: ");
    scanf("%d", &count);

    printf("Enter the elements:\n");
    for (int i = 0; i < count; i++) {
        scanf("%d", &numbers[i]);
    }

    // Convert numbers to strings for execvp
    char *args[MAX_NUMBERS + 2];
    args[0] = "./sort";
    char str_nums[count][20]; // Array to store string versions of numbers
    for (int i = 0; i < count; i++) {
        sprintf(str_nums[i], "%d", numbers[i]);
        args[i + 1] = str_nums[i];
    }
    args[count + 1] = NULL; // NULL-terminate the args array

    // Create a pipe for communication between child and parent
    int pipefd[2];
    if (pipe(pipefd) == -1) {
        perror("pipe");
        exit(EXIT_FAILURE);
    }

    // Create child process
    pid_t pid = fork();

    if (pid < 0) {
        // Error handling
        perror("Fork failed");
        exit(1);
    } 
    else if (pid == 0) {
        // Child process
        close(pipefd[0]); // Close unused read end

        // Redirect stdout to pipe
        dup2(pipefd[1], STDOUT_FILENO);
        close(pipefd[1]);

        // Execute sort program
        execvp(args[0], args);

        // If execvp returns, it means there was an error
        perror("execvp");
        exit(EXIT_FAILURE);
    } 
    else {
        // Parent process
        close(pipefd[1]); // Close unused write end

        // Wait for child to complete
        wait(NULL);

        // Read sorted output from pipe
        char buffer[MAX_LINE_LENGTH];
        memset(buffer, 0, sizeof(buffer));

        ssize_t bytes_read = read(pipefd[0], buffer, sizeof(buffer) - 1);
        if (bytes_read == -1) {
            perror("read from pipe");
            exit(EXIT_FAILURE);
        }
        buffer[bytes_read] = '\0';
        close(pipefd[0]);

        // Print the sorted output received from the sort program
        printf("Sorted array: %s", buffer);

        // Parse sorted numbers from buffer
        int sorted_numbers[MAX_NUMBERS];
        int num_count = 0;
        char *token = strtok(buffer, " \n");
        while (token != NULL && num_count < MAX_NUMBERS) {
            sorted_numbers[num_count++] = atoi(token);
            token = strtok(NULL, " \n");
        }

        // Prepare arguments for oddeven program
        char *oddeven_args[num_count + 2];
        oddeven_args[0] = "./oddeven";
        char sorted_str_nums[num_count][20]; // Array to store string versions of sorted numbers
        for (int i = 0; i < num_count; i++) {
            sprintf(sorted_str_nums[i], "%d", sorted_numbers[i]);
            oddeven_args[i + 1] = sorted_str_nums[i];
        }
        oddeven_args[num_count + 1] = NULL; // NULL-terminate the args array

        // Execute oddeven program
        execvp(oddeven_args[0], oddeven_args);

        // If execvp returns, it means there was an error
        perror("execvp");
        exit(EXIT_FAILURE);
    }

    return 0;
}
