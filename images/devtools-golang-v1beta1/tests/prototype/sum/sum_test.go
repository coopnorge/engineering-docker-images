package sum

import (
	"testing"
)

func TestSum(t *testing.T) {
	if Sum(2, 2) != 4 {
		t.Fatalf("2 + 2 != 4")
	}
}
