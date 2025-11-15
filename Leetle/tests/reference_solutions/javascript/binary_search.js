/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number}
 */
function search(nums, target) {
    let left = 0, right = nums.length - 1;
    while (left <= right) {
        const mid = Math.floor((left + right) / 2);
        if (nums[mid] === target) {
            return mid;
        } else if (nums[mid] < target) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    return -1;
}

// Main function to handle input from stdin
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
const lines = input.split('\n');

// Parse array (first line)
const nums = JSON.parse(lines[0].trim());

// Parse target (second line)
const target = parseInt(lines[1].trim());

const result = search(nums, target);
console.log(result);
