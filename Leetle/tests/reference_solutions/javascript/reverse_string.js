/**
 * @param {character[]} s
 * @return {void} Do not return anything, modify s in-place instead.
 */
function reverseString(s) {
    let left = 0, right = s.length - 1;
    while (left < right) {
        [s[left], s[right]] = [s[right], s[left]];
        left++;
        right--;
    }
}

// Main function to handle input from stdin
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
const s = JSON.parse(input);

reverseString(s);
console.log(JSON.stringify(s));
