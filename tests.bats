#!/usr/bin/env bats

numLines=64
testCasePoints=5

setup()
{
	PATH=$(pwd):$PATH
}

teardown()
{
	rm -f testOutput.txt
}

diff_files()
{
	diff -b -B -Z -y -w -i --strip-trailing-cr --suppress-common-lines $1 $2 
}

@test "compiletest" {
	make all
	run which p
	[ "$status" -eq 0 ]
}

@test "test1" {
        p < tests/input1.txt > testOutput.txt
        count=$(diff -b -B -Z -y -w -i --strip-trailing-cr --suppress-common-lines testOutput.txt tests/output1.txt | wc -l)
        score=$(bc -l <<<"(($numLines - $count) / $numLines) * $testCasePoints")
        echo -e "\x1F$score"
        diff -b -B -Z -y -w -i --strip-trailing-cr --suppress-common-lines testOutput.txt tests/output1.txt
}


@test "testclean" {
	make clean
	run which p
	[ "$status" -ne 0 ]
}
