factorial(){
    echo "Enter a number "
    read n
    i=1
    fac=1
    while [ $i -le $n ]; do
	fac=$((fac*i))
	((i++))
    done
    echo $fac
    
    
}
echo "Enter the first number"
read a
echo "Enter the second number"
read b
sum=$((a+b))
echo "The sum is $sum"
factorial
