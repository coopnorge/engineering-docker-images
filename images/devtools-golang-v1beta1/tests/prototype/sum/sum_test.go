package sum_test

import (
	"prototype/sum"
	"testing"
)

func TestSum(t *testing.T) {
	if sum.Sum(2, 2) != 4 {
		t.Fatalf("2 + 2 != 4")
	}
}
