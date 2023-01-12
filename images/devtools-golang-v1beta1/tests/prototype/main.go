package main

import (
	"fmt"
	"os"

	"example.com/prototype/sum"
)

func main() {
	fmt.Println("2 + 2 =", sum.Sum(2, 2))
	fmt.Println("os.Args =", os.Args)
}
