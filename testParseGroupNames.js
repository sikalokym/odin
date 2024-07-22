// Define the parseGroupNames function
const parseGroupNames = (groups) => {
    return groups.map(group => {
        const match = group.match(/odin-([\w-]+)-(\w+)/);
        return match ? { country: match[1], role: match[2] } : null;
    }).filter(Boolean);
};

// Test data
const testGroups = [
    'odin-switzerland-readers',
    'odin-italy-modifiers',
    'odin-ireland-readers',
    'odin-spain-readers',
    'odin-belgium-readers',
    'odin-spain-modifiers',
    'odin-france-readers',
    'odin-austria-readers',
    'odin-germany-readers',
    'odin-france-modifiers',
    'odin-austria-modifiers',
    'odin-germany-modifiers',
    'odin-italy-readers',
    'odin-ireland-modifiers',
    'odin-belgium-modifiers',
    'odin-switzerland-modifiers',
    'odin-united-kingdom-readers',
    'odin-united-kingdom-modifiers'
];

// Run the function and log the results
const parsedGroups = parseGroupNames(testGroups);
console.log(parsedGroups);
