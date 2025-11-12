.PHONY: sanity orr all t2 t3 t4 t5 t6 t7 t8

sanity:
	bin/orr_sanity.sh

orr: all

all: t2 t3 t4 t5 t6 t7 t8
	bin/orr_all.sh --fail-fast

t2:
	bin/orr_t2.sh

t3:
	bin/orr_t3.sh

t4:
	bin/orr_t4.sh

t5:
	bin/orr_t5.sh

t6:
	bin/orr_t6.sh

t7:
	bin/orr_t7.sh

t8:
	bin/orr_t8.sh
