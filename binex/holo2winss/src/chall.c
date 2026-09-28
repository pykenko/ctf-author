#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

void init(){
	setvbuf(stdin, NULL, _IONBF, 0);
	setvbuf(stdout, NULL, _IONBF, 0);
}

int adminPass;

void printArt() {
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣤⣴⣶⣶⣶⣶⣶⣶⣶⣶⣶⣶⣦⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⠿⠛⠛⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠙⠛⠻⣿⣶⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣶⡿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠿⣷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⢀⣼⡿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣷⣄⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⢀⣾⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣶⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⡀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣆⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⣾⣟⣀⠀⠀⠀⠀⣀⣀⠀⠀⠀⢸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣿⡇⠀⠀⢀⣄⠀⠀⠀⠀⣀⣹⣿⡆⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⢀⣤⣾⡿⣿⣟⣿⣷⠀⠀⠀⣿⣿⣤⣤⣤⣼⣿⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣿⣧⣤⣤⣼⣿⠀⠀⠀⢸⣿⣻⣿⠿⣷⣦⣄⠀⠀\n");
    printf("⢀⣴⡿⠋⠁⠀⠙⢻⣿⡇⠀⠀⠀⣿⡟⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⠉⢹⣿⠀⠀⠀⠈⣿⣿⠋⠀⠀⠙⢿⣷⣄\n");
    printf("⣿⣿⣶⣦⠀⠀⢠⣿⣿⠅⠀⠀⠀⣿⡇⠀⣠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠀⠘⣿⡇⠀⠀⠀⣿⣿⣆⠀⠀⢰⣶⣿⣿\n");
    printf("⠀⠀⣿⡇⢀⣴⣿⢿⣿⡄⠀⠀⠀⣿⡇⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣿⣷⠀⠀⠀⢻⣿⢿⣧⡀⠘⣿⠃⠀\n");
    printf("⠀⠀⣿⣷⣿⣿⠁⣸⣿⠇⠀⠀⠀⣿⡇⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⠀⠀⣿⡇⡄⠀⠀⢸⣿⠈⣿⣿⣶⣿⠇⠀\n");
    printf("⠀⠀⠘⠉⢸⣿⠀⣿⡟⢰⠀⠀⠀⣿⡇⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠀⠀⣿⡇⢡⠀⠀⠸⣿⡄⢸⣿⠈⠉⠀⠀\n");
    printf("⠀⠀⠀⠀⣼⡟⠀⣿⡇⠸⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⢀⣤⣄⣀⣤⡄⠀⠀⠀⠀⠀⠀⠀⢠⣿⡇⠀⡄⠀⠘⣿⡇⢸⣿⡀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⣿⡇⢠⣿⡇⠀⣆⠀⠀⣿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⢡⡀⠀⣿⣇⠈⣿⡇⠀⠀⠀\n");
    printf("⠀⠀⠀⢸⣿⠃⢸⣿⣶⡿⣿⣆⠀⣿⣿⣤⣤⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣤⣤⣾⣿⠀⣠⣿⣿⣷⣿⣿⠀⣿⣧⠀⠀⠀\n");
    printf("⠀⠀⠀⣼⣿⠀⠘⠛⠉⠀⢿⣿⣷⣿⣿⣿⠉⠛⠛⠛⠻⣿⣿⠿⠿⠿⠿⣿⣿⡿⠛⠛⠛⠛⢹⣿⣿⣴⣿⡿⠃⠈⠙⠛⠀⢸⣿⠀⠀⠀\n");
    printf("⠀⠀⢠⣿⡇⠀⠀⠀⠀⠀⢀⣨⣿⠟⣿⣿⣶⣦⣤⣄⣀⡈⠻⣷⣄⢠⣾⡿⠋⣀⣀⣠⣤⣶⣾⣿⡟⣿⣧⡀⠀⠀⠀⠀⠀⠘⣿⡇⠀⠀\n");
    printf("⠀⠀⢸⣿⠁⠀⢀⡀⡠⠒⣱⣿⠏⠀⣿⡇⠈⠉⠙⠛⠻⠿⠿⢿⣿⣿⣿⡿⠿⠿⠛⠛⠛⠛⠉⠉⠈⠉⢿⣿⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀\n");
    printf("⠀⢀⣿⣇⣤⣶⣿⡿⠀⣠⣿⠏⠀⢸⣿⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⠼⣿⣄⠤⠔⠚⣿⣆⣹⣿⠀⠀⠀⠀\n");
    printf("⠀⠈⠛⠛⠋⢉⣿⠇⢠⣿⠟⠀⠀⣸⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣴⡇⣿⡇⠀⠀⠀⠀⠀⠘⣿⡇⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⢸⣿⣠⣿⡟⠒⠤⢀⣿⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⡾⠋⠀⠀⠀⠀⠀⠀⠀⠀⢻⣷⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠙⠛⠟⣿⣿⣶⣤⣤⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⠊⠁⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⡇⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⣿⣇⠈⢩⣿⣿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠔⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⠇⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⠿⠿⣻⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⠧⣀⣀⡀⣀⣀⣀⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀⢸⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣏⠐⠠⢄⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⡠⠤⠒⢉⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣷⣦⣄⣀⡈⠉⠁⠐⠒⠒⠒⠒⠒⠒⠀⠉⢁⣀⣀⣤⣶⡿⢿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⡇⠿⠿⣿⣿⣷⣶⣶⣶⣶⣶⣿⣿⡿⠿⠟⣿⣟⡁⠀⠈⠻⣷⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣧⠀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⢰⣿⠿⢿⣷⣶⣴⡟⠛⠛⠛⠿⣿⣦⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⣿⡀⠀⣿⡇⠀⠀⠀⠀⠀⠀⠀⣿⡇⠀⣾⣿⠁⠀⠀⢸⣿⠃⣼⣿⣿⠿⠿⠋⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣶⡿⠻⣿⣦⣿⡇⠀⠀⠀⠀⠀⠀⠀⣿⣧⣾⡟⠻⣷⣄⠀⢸⣿⣠⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀\n");
    printf("⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠺⠿⠿⠿⠿⠿⠿⠇⠀⠀⠀⠀⠀⠀⠀⠿⠿⠿⠿⠿⠿⠿⠀⠈⠻⠿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀\n");
    puts("before gawr gura graduate :(");
}

void showProfile(){
    system("clear");
    puts("username : Auric");
    puts("desc : Biboo has me out here watching 4-hour Minecraft VODs like it’s a religious experience, and every time she says “let’s gooo” I physically ascend. Fuwawa and Mococo? Actual menaces. I hear “baoo baoo” and suddenly I’m kicking my feet, giggling, and questioning my dignity. They’ve infected my brain like a virus made of fluff and bark. And Kronii?? She looks at the camera and I forget how to function. I would let her manipulate my timeline, gaslight me, destroy my schedule, and call me pathetic—and I’d say thank you. I’m not even a person anymore. I’m just a shrine to their unholy power.");
    getchar();
}

void admin_get_secret(){
    int data;
    printf("Username : admin\n");
    printf("Password : \n");
    scanf("%d", &data);
    if(data == adminPass){
        FILE *file = fopen("kronichiwa.hololive", "r");
        char line[256];
        if (fgets(line, sizeof(line), file) != NULL) {
            printf("%s\n", line);
        }
        fclose(file);
    }
    getchar();
    getchar();
}

void list_all_password(){
    printf("auric -> \"kronipleasenoticeme1\"\n");
    printf("admin -> \"%d\"\n", adminPass);
    char continues[64];
    scanf("%s", continues);
}

void manage_acc(){
    puts("Account manager BETA 1.0");
    puts("Change Username [still on BETA]");
    char username[64];
    scanf("%s", username);
}

int main(){
    init();
    srand(time(NULL));
    adminPass = rand() % 90000 + 10000;
    while(1){
        puts("Welcome to my HOLOLIVE fanbase");
        puts("The best fanbase ever created");
        puts("what do you want to do?");
        puts("1. Show profile");
        puts("2. List favourites");
        puts("3. List talents");
        puts("4. Watch a live");
        puts("5. Manage your account");
        puts("6. Exit");
        char user_input[100];
        fgets(user_input, sizeof(user_input), stdin);
        if(strcmp(user_input, "1\n") == 0){
            showProfile();
        } else if(strcmp(user_input, "6\n") == 0){
            return 0;
        } else if(strcmp(user_input, "4\n") == 0){
            system("clear");
            printArt();
            getchar();
        } else if(strcmp(user_input, "2\n") == 0){
            printf("\n1. Kroni\n2. Biboo\n3. Fuwawa and Mococo");
            getchar();
        } else if(strcmp(user_input, "3\n") == 0){
            system("clear");
            printf("Hololive Talents:\n");
            printf("1. Tokino Sora\n");
            printf("2. Roboco-san\n");
            printf("3. Sakura Miko\n");
            printf("4. Hoshimachi Suisei\n");
            printf("5. Azuki Kiryu\n");
            printf("6. Inugami Korone\n");
            printf("7. Nekomata Okayu\n");
            printf("8. Usada Pekora\n");
            printf("9. Shiranui Flare\n");
            printf("10. Kiryuu Coco\n");
            printf("11. Amane Kanata\n");
            printf("12. Kiryu Coco\n");
            printf("13. Tsukumo Sana\n");
            printf("14. Mori Calliope\n");
            printf("15. Takanashi Kiara\n");
            printf("16. Ouro Kronii\n");
            printf("17. Nanashi Mumei\n");
            printf("18. Hakos Baelz\n");
            printf("19. Irys\n");
            printf("20. Michael Aurelio\n");
            getchar();
        } else if(strcmp(user_input, "5\n") == 0){
            manage_acc();
        } else if(strcmp(user_input, "adminBetaSecretCommand\n") == 0){
            printf("%p\n", list_all_password);
            printf("%p", admin_get_secret);
        }
    }
}