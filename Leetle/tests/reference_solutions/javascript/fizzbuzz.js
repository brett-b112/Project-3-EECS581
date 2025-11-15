/**
 * @param {number} n
 * @return {string[]}
 */
function fizzBuzz(n) {
    const result = [];
    for (let i = 1; i <= n; i++) {
        if (i % 15 === 0) {
            result.push("FizzBuzz");
        } else if (i % 3 === 0) {
            result.push("Fizz");
        } else if (i % 5 === 0) {
            result.push("Buzz");
        } else {
            result.push(i.toString());
        }
    }
    return result;
}

// Main function to handle input from stdin
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
const n = parseInt(input);

const result = fizzBuzz(n);
console.log(JSON.stringify(result));
