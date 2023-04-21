setup:
	./setup.sh

# Example usage: 
#   $ make setup
#   $ python3 nocap.py -t test_exp_log -f log
#   $ make compare_exp_log FUNC=log

reg_%: test/test_%.c
	gcc -o outputs/$@ $^ -lm

nocap_%: build/src/test_%_lookups.c
	gcc -o outputs/$@ $^ build/src/nocap_$(FUNC).c -lm

compare_%: nocap_% reg_%
	@echo "Comparing nocap_$* with (baseline) reg_$*"
	@echo "-------------------------------------"
	@echo "------------- nocap_$* --------------"
	@time outputs/nocap_$*
	@echo "------------- reg_$* --------------"
	@time outputs/reg_$*

clean: 
	rm -rf outputs/*