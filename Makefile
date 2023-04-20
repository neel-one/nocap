# Example run: `make compare_exp`

reg_%: test/test_%.c
	gcc -o outputs/$@ $^ -lm

nocap_%: build/src/nocap_%.c build/src/test_%_lookups.c
	@python3 nocap.py -f $* build
	gcc -o outputs/$@ $^

compare_%: nocap_% reg_%
	@echo "Comparing nocap_$* with (baseline) reg_$*"
	@echo "-------------------------------------"
	@echo "------------- nocap_$* --------------"
	@time outputs/nocap_$*
	@echo "------------- reg_$* --------------"
	@time outputs/reg_$*

clean: 
	rm -rf outputs/*