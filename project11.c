#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <sys/types.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <time.h>

#define MAGIC_NUMBER 0xD34D
#define BLOCK_SIZE 4096
#define TOTAL_BLOCKS 64
#define INODE_SIZE 256
#define INODE_COUNT 80
#define SUPERBLOCK_NUM 0
#define INODE_BITMAP_NUM 1
#define DATA_BITMAP_NUM 2
#define INODE_TABLE_START 3
#define DATA_BLOCK_START 8

typedef struct {
    uint16_t magic;
    uint32_t block_size;
    uint32_t total_blocks;
    uint32_t inode_bitmap_block;
    uint32_t data_bitmap_block;
    uint32_t inode_table_start;
    uint32_t data_block_start;
    uint32_t inode_size;
    uint32_t inode_count;
    uint8_t reserved[4058];
} superblock_t;

typedef struct {
    uint32_t mode;
    uint32_t uid;
    uint32_t gid;
    uint32_t size;
    uint32_t atime;
    uint32_t ctime;
    uint32_t mtime;
    uint32_t dtime;
    uint32_t links_count;
    uint32_t blocks_count;
    uint32_t direct_ptr;
    uint32_t single_indirect;
    uint32_t double_indirect;
    uint32_t triple_indirect;
    uint8_t reserved[156];
} inode_t;

superblock_t superblock;
uint8_t inode_bitmap[BLOCK_SIZE];
uint8_t data_bitmap[BLOCK_SIZE];
inode_t inodes[INODE_COUNT];
int fs_fd;

void read_block(int block_num, void *buffer) {
    lseek(fs_fd, block_num * BLOCK_SIZE, SEEK_SET);
    read(fs_fd, buffer, BLOCK_SIZE);
}

void write_block(int block_num, void *buffer) {
    lseek(fs_fd, block_num * BLOCK_SIZE, SEEK_SET);
    write(fs_fd, buffer, BLOCK_SIZE);
}

bool is_bit_set(uint8_t *bitmap, int index) {
    int byte_index = index / 8;
    int bit_index = index % 8;
    return (bitmap[byte_index] & (1 << bit_index)) != 0;
}

void set_bit(uint8_t *bitmap, int index) {
    int byte_index = index / 8;
    int bit_index = index % 8;
    bitmap[byte_index] |= (1 << bit_index);
}

void clear_bit(uint8_t *bitmap, int index) {
    int byte_index = index / 8;
    int bit_index = index % 8;
    bitmap[byte_index] &= ~(1 << bit_index);
}

void read_inodes() {
    uint8_t buffer[BLOCK_SIZE];
    int inodes_per_block = BLOCK_SIZE / INODE_SIZE;

    for (int i = 0; i < 5; i++) {
        read_block(INODE_TABLE_START + i, buffer);
        for (int j = 0; j < inodes_per_block && (i * inodes_per_block + j) < INODE_COUNT; j++) {
            memcpy(&inodes[i * inodes_per_block + j], buffer + j * INODE_SIZE, INODE_SIZE);
        }
    }
}

void write_inodes() {
    uint8_t buffer[BLOCK_SIZE];
    int inodes_per_block = BLOCK_SIZE / INODE_SIZE;

    for (int i = 0; i < 5; i++) {
        memset(buffer, 0, BLOCK_SIZE);
        for (int j = 0; j < inodes_per_block && (i * inodes_per_block + j) < INODE_COUNT; j++) {
            memcpy(buffer + j * INODE_SIZE, &inodes[i * inodes_per_block + j], INODE_SIZE);
        }
        write_block(INODE_TABLE_START + i, buffer);
    }
}

bool validate_superblock() {
    printf("Validating superblock...\n");
    bool is_valid = true;

    if (superblock.magic != MAGIC_NUMBER) {
        printf("ERROR: Invalid magic number: 0x%X (expected: 0x%X)\n", superblock.magic, MAGIC_NUMBER);
        superblock.magic = MAGIC_NUMBER;
        is_valid = false;
    }

    if (superblock.block_size != BLOCK_SIZE) {
        printf("ERROR: Invalid block size: %u (expected: %u)\n", superblock.block_size, BLOCK_SIZE);
        superblock.block_size = BLOCK_SIZE;
        is_valid = false;
    }

    if (superblock.total_blocks != TOTAL_BLOCKS) {
        printf("ERROR: Invalid total blocks: %u (expected: %u)\n", superblock.total_blocks, TOTAL_BLOCKS);
        superblock.total_blocks = TOTAL_BLOCKS;
        is_valid = false;
    }

    if (superblock.inode_bitmap_block != INODE_BITMAP_NUM) {
        printf("ERROR: Invalid inode bitmap block: %u (expected: %u)\n", superblock.inode_bitmap_block, INODE_BITMAP_NUM);
        superblock.inode_bitmap_block = INODE_BITMAP_NUM;
        is_valid = false;
    }

    if (superblock.data_bitmap_block != DATA_BITMAP_NUM) {
        printf("ERROR: Invalid data bitmap block: %u (expected: %u)\n", superblock.data_bitmap_block, DATA_BITMAP_NUM);
        superblock.data_bitmap_block = DATA_BITMAP_NUM;
        is_valid = false;
    }

    if (superblock.inode_table_start != INODE_TABLE_START) {
        printf("ERROR: Invalid inode table start: %u (expected: %u)\n", superblock.inode_table_start, INODE_TABLE_START);
        superblock.inode_table_start = INODE_TABLE_START;
        is_valid = false;
    }

    if (superblock.data_block_start != DATA_BLOCK_START) {
        printf("ERROR: Invalid data block start: %u (expected: %u)\n", superblock.data_block_start, DATA_BLOCK_START);
        superblock.data_block_start = DATA_BLOCK_START;
        is_valid = false;
    }

    if (superblock.inode_size != INODE_SIZE) {
        printf("ERROR: Invalid inode size: %u (expected: %u)\n", superblock.inode_size, INODE_SIZE);
        superblock.inode_size = INODE_SIZE;
        is_valid = false;
    }

    if (superblock.inode_count != INODE_COUNT) {
        printf("ERROR: Invalid inode count: %u (expected: %u)\n", superblock.inode_count, INODE_COUNT);
        superblock.inode_count = INODE_COUNT;
        is_valid = false;
    }

    return is_valid;
}

// Helper to process indirect blocks
void process_indirect_block(uint32_t indirect_block_num, uint8_t *calculated_bitmap) {
    uint32_t pointers[BLOCK_SIZE / sizeof(uint32_t)];
    read_block(indirect_block_num, pointers);

    for (int i = 0; i < BLOCK_SIZE / sizeof(uint32_t); i++) {
        uint32_t block_num = pointers[i];
        if (block_num != 0 && block_num >= DATA_BLOCK_START && block_num < TOTAL_BLOCKS) {
            set_bit(calculated_bitmap, block_num);
        }
    }
}

bool check_data_bitmap_consistency() {
    printf("Checking data bitmap consistency...\n");
    bool is_consistent = true;

    uint8_t calculated_bitmap[BLOCK_SIZE];
    memset(calculated_bitmap, 0, BLOCK_SIZE);

    // Mark reserved blocks (blocks before first data block) as used
    for (int i = 0; i < DATA_BLOCK_START; i++) {
        set_bit(calculated_bitmap, i);
    }

    for (int i = 0; i < INODE_COUNT; i++) {
        inode_t *inode = &inodes[i];

        if (inode->links_count > 0 && inode->dtime == 0) {

            // Direct pointer
            if (inode->direct_ptr != 0) {
                if (inode->direct_ptr < DATA_BLOCK_START || inode->direct_ptr >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has invalid direct pointer: %u\n", i, inode->direct_ptr);
                    inode->direct_ptr = 0;
                    is_consistent = false;
                } else {
                    set_bit(calculated_bitmap, inode->direct_ptr);
                }
            }

            // Single indirect pointer
            if (inode->single_indirect != 0) {
                if (inode->single_indirect < DATA_BLOCK_START || inode->single_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has invalid single indirect pointer: %u\n", i, inode->single_indirect);
                    inode->single_indirect = 0;
                    is_consistent = false;
                } else {
                    set_bit(calculated_bitmap, inode->single_indirect);
                    process_indirect_block(inode->single_indirect, calculated_bitmap);
                }
            }

            // Double indirect pointer
            if (inode->double_indirect != 0) {
                if (inode->double_indirect < DATA_BLOCK_START || inode->double_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has invalid double indirect pointer: %u\n", i, inode->double_indirect);
                    inode->double_indirect = 0;
                    is_consistent = false;
                } else {
                    set_bit(calculated_bitmap, inode->double_indirect);
                    process_indirect_block(inode->double_indirect, calculated_bitmap);
                }
            }

            // Triple indirect pointer
            if (inode->triple_indirect != 0) {
                if (inode->triple_indirect < DATA_BLOCK_START || inode->triple_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has invalid triple indirect pointer: %u\n", i, inode->triple_indirect);
                    inode->triple_indirect = 0;
                    is_consistent = false;
                } else {
                    set_bit(calculated_bitmap, inode->triple_indirect);
                    process_indirect_block(inode->triple_indirect, calculated_bitmap);
                }
            }
        }
    }

    // Compare calculated vs actual data bitmap
    for (int i = DATA_BLOCK_START; i < TOTAL_BLOCKS; i++) {
        if (is_bit_set(data_bitmap, i) && !is_bit_set(calculated_bitmap, i)) {
            printf("ERROR: Block %d is marked as used in data bitmap but not referenced by any inode\n", i);
            clear_bit(data_bitmap, i);
            is_consistent = false;
        } else if (!is_bit_set(data_bitmap, i) && is_bit_set(calculated_bitmap, i)) {
            printf("ERROR: Block %d is referenced by an inode but not marked as used in data bitmap\n", i);
            set_bit(data_bitmap, i);
            is_consistent = false;
        }
    }

    return is_consistent;
}

bool check_inode_bitmap_consistency() {
    printf("Checking inode bitmap consistency...\n");
    bool is_consistent = true;

    uint8_t calculated_bitmap[BLOCK_SIZE];
    memset(calculated_bitmap, 0, BLOCK_SIZE);

    for (int i = 0; i < INODE_COUNT; i++) {
        if (inodes[i].links_count > 0 && inodes[i].dtime == 0) {
            set_bit(calculated_bitmap, i);
        }
    }

    for (int i = 0; i < INODE_COUNT; i++) {
        if (is_bit_set(inode_bitmap, i) && !is_bit_set(calculated_bitmap, i)) {
            printf("ERROR: Inode %d is marked as used in inode bitmap but is not valid\n", i);
            clear_bit(inode_bitmap, i);
            is_consistent = false;
        } else if (!is_bit_set(inode_bitmap, i) && is_bit_set(calculated_bitmap, i)) {
            printf("ERROR: Inode %d is valid but not marked as used in inode bitmap\n", i);
            set_bit(inode_bitmap, i);
            is_consistent = false;
        }
    }

    return is_consistent;
}

bool check_duplicate_blocks() {
    printf("Checking for duplicate blocks...\n");
    bool no_duplicates = true;

    int block_user[TOTAL_BLOCKS];
    for (int i = 0; i < TOTAL_BLOCKS; i++) {
        block_user[i] = -1;
    }

    for (int i = 0; i < INODE_COUNT; i++) {
        if (inodes[i].links_count > 0 && inodes[i].dtime == 0) {
            if (inodes[i].direct_ptr != 0) {
                if (inodes[i].direct_ptr >= DATA_BLOCK_START && inodes[i].direct_ptr < TOTAL_BLOCKS) {
                    if (block_user[inodes[i].direct_ptr] == -1) {
                        block_user[inodes[i].direct_ptr] = i;
                    } else {
                        printf("ERROR: Block %u is referenced by both inode %d and inode %d\n",
                               inodes[i].direct_ptr, block_user[inodes[i].direct_ptr], i);
                        inodes[i].direct_ptr = 0;
                        no_duplicates = false;
                    }
                }
            }

            if (inodes[i].single_indirect != 0) {
                if (inodes[i].single_indirect >= DATA_BLOCK_START && inodes[i].single_indirect < TOTAL_BLOCKS) {
                    if (block_user[inodes[i].single_indirect] == -1) {
                        block_user[inodes[i].single_indirect] = i;
                    } else {
                        printf("ERROR: Block %u is referenced by both inode %d and inode %d\n",
                               inodes[i].single_indirect, block_user[inodes[i].single_indirect], i);
                        inodes[i].single_indirect = 0;
                        no_duplicates = false;
                    }
                }
            }

            if (inodes[i].double_indirect != 0) {
                if (inodes[i].double_indirect >= DATA_BLOCK_START && inodes[i].double_indirect < TOTAL_BLOCKS) {
                    if (block_user[inodes[i].double_indirect] == -1) {
                        block_user[inodes[i].double_indirect] = i;
                    } else {
                        printf("ERROR: Block %u is referenced by both inode %d and inode %d\n",
                               inodes[i].double_indirect, block_user[inodes[i].double_indirect], i);
                        inodes[i].double_indirect = 0;
                        no_duplicates = false;
                    }
                }
            }

            if (inodes[i].triple_indirect != 0) {
                if (inodes[i].triple_indirect >= DATA_BLOCK_START && inodes[i].triple_indirect < TOTAL_BLOCKS) {
                    if (block_user[inodes[i].triple_indirect] == -1) {
                        block_user[inodes[i].triple_indirect] = i;
                    } else {
                        printf("ERROR: Block %u is referenced by both inode %d and inode %d\n",
                               inodes[i].triple_indirect, block_user[inodes[i].triple_indirect], i);
                        inodes[i].triple_indirect = 0;
                        no_duplicates = false;
                    }
                }
            }
        }
    }

    return no_duplicates;
}

bool check_bad_blocks() {
    printf("Checking for bad blocks...\n");
    bool no_bad_blocks = true;

    for (int i = 0; i < INODE_COUNT; i++) {
        if (inodes[i].links_count > 0 && inodes[i].dtime == 0) {
            if (inodes[i].direct_ptr != 0) {
                if (inodes[i].direct_ptr < DATA_BLOCK_START || inodes[i].direct_ptr >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has bad direct block pointer: %u (valid range: %u-%u)\n",
                           i, inodes[i].direct_ptr, DATA_BLOCK_START, TOTAL_BLOCKS - 1);
                    inodes[i].direct_ptr = 0;
                    no_bad_blocks = false;
                }
            }

            if (inodes[i].single_indirect != 0) {
                if (inodes[i].single_indirect < DATA_BLOCK_START || inodes[i].single_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has bad single indirect block pointer: %u (valid range: %u-%u)\n",
                           i, inodes[i].single_indirect, DATA_BLOCK_START, TOTAL_BLOCKS - 1);
                    inodes[i].single_indirect = 0;
                    no_bad_blocks = false;
                }
            }

            if (inodes[i].double_indirect != 0) {
                if (inodes[i].double_indirect < DATA_BLOCK_START || inodes[i].double_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has bad double indirect block pointer: %u (valid range: %u-%u)\n",
                           i, inodes[i].double_indirect, DATA_BLOCK_START, TOTAL_BLOCKS - 1);
                    inodes[i].double_indirect = 0;
                    no_bad_blocks = false;
                }
            }

            if (inodes[i].triple_indirect != 0) {
                if (inodes[i].triple_indirect < DATA_BLOCK_START || inodes[i].triple_indirect >= TOTAL_BLOCKS) {
                    printf("ERROR: Inode %d has bad triple indirect block pointer: %u (valid range: %u-%u)\n",
                           i, inodes[i].triple_indirect, DATA_BLOCK_START, TOTAL_BLOCKS - 1);
                    inodes[i].triple_indirect = 0;
                    no_bad_blocks = false;
                }
            }
        }
    }

    return no_bad_blocks;
}

void check_and_fix_fs_image(const char *filename) {
    printf("Checking file system image: %s\n", filename);

    fs_fd = open(filename, O_RDWR);
    if (fs_fd == -1) {
        perror("Failed to open file system image");
        exit(1);
    }

    read_block(SUPERBLOCK_NUM, &superblock);
    read_block(INODE_BITMAP_NUM, inode_bitmap);
    read_block(DATA_BITMAP_NUM, data_bitmap);
    read_inodes();

    bool superblock_valid = validate_superblock();
    if (!superblock_valid) {
        printf("Fixed superblock issues\n");
        write_block(SUPERBLOCK_NUM, &superblock);
    }

    bool no_bad_blocks = check_bad_blocks();
    if (!no_bad_blocks) {
        printf("Fixed bad block issues\n");
        write_inodes();
    }

    bool no_duplicates = check_duplicate_blocks();
    if (!no_duplicates) {
        printf("Fixed duplicate block issues\n");
        write_inodes();
    }

    bool data_bitmap_consistent = check_data_bitmap_consistency();
    if (!data_bitmap_consistent) {
        printf("Fixed data bitmap inconsistencies\n");
        write_block(DATA_BITMAP_NUM, data_bitmap);
    }

    bool inode_bitmap_consistent = check_inode_bitmap_consistency();
    if (!inode_bitmap_consistent) {
        printf("Fixed inode bitmap inconsistencies\n");
        write_block(INODE_BITMAP_NUM, inode_bitmap);
    }

    if (superblock_valid && data_bitmap_consistent && inode_bitmap_consistent && no_duplicates && no_bad_blocks) {
        printf("No errors found or all errors have been fixed!\n");
    } else {
        printf("All errors have been fixed. Re-run the checker to verify.\n");
    }

    close(fs_fd);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        printf("Usage: %s <file_system_image>\n", argv[0]);
        return 1;
    }

    check_and_fix_fs_image(argv[1]);
    return 0;
}
