
// c99 comment

struct s {
    int x;
    int y[3];
    char z[x];
};


struct something {
	s my_s;
	bool is_truth;
};

struct child : something {
	int w;
	uint32_t t[0x10];
};

struct grand_child(0x3333) : child {
	int r;
};
