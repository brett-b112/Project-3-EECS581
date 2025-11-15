/**
 * @param {number[]} nums
 * @param {number} target
 * @return {number[]}
 */
function twoSum(nums, target) {
    const numMap = new Map();
    for (let i = 0; i < nums.length; i++) {
        const complement = target - nums[i];
        if (numMap.has(complement)) {
            return [numMap.get(complement), i];
        }
        numMap.set(nums[i], i);
    }
    return [];
}

// Main function to handle input from stdin
const fs = require('fs');
const input = fs.readFileSync(0, 'utf-8').trim();
const lines = input.split('\n');

// Parse array (first line)
const nums = JSON.parse(lines[0].trim());

// Parse target (second line)
const target = parseInt(lines[1].trim());

const result = twoSum(nums, target);
console.log(JSON.stringify(result));
