/**
 * @param {number} x
 * @return {boolean}
 */
function isPalindrome(x) {
    if (x < 0) return false;
    const str = x.toString();
    return str === str.split('').reverse().join('');
}

// Main function to handle input from stdin
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
const x = parseInt(input);

const result = isPalindrome(x);
console.log(result.toString());
