// This Node.js script uses list_attr_celeba.txt and identity_CelebA.txt (ensure they exist) to pick out a few train and test images as the default dataset is excessive
// Identities are picked based on if they have at least X amount of images available that are "difficult" (fall into specific categories)
// Those "difficult" images are taken into the test set, and the least difficult ones are used for training
// Identities with not enough "difficult" images are not used

// IMPORTANT: Keep a separate copy of the original img_celeba folder elsewhere, as this script will modify it and delete many files

const fs = require('fs')

const difficultCategories = ['Blurry', 'Eyeglasses', 'Wearing_Hat']
const numTrainImages = 5
const numTestImages = 3
const minDifficultImages = 2 // How many of the test images must be in a difficult category for the identity to be considered

console.log('Preparing dataset; this might take a while...')

// STEP 0: Ensure the required files are in place (does not check images)
if (!fs.existsSync('list_attr_celeba.txt') || !fs.existsSync('identity_CelebA.txt') || !fs.existsSync('img_celeba') || !fs.statSync('img_celeba').isDirectory()) {
    console.error('Error: Some files missing! Check that you have the img_celeba folder of images, along with list_attr_celeba.txt and identity_CelebA.txt in the same directory as this script.')
    process.exit(1)
}

// STEP 1: If needed, parse the data from the list_attr_celeba.txt and identity_CelebA.txt files into a JSON that is easier to work with
if (!fs.existsSync('data.json')) {
    // Read the categories data file and create the categories array
    const categoryData = fs.readFileSync('list_attr_celeba.txt').toString().split('\n').map(line => line.split(' ').map(word => word.trim()).filter(word => word.length > 0)).slice(1)
    const categories = categoryData[0]

    // Use that to create a Map of files, with each file and an array of its categories
    const filesWithCategories = new Map()
    categoryData.forEach(line => {
        const file = line[0]
        const cats = []
        for (let i = 1; i < line.length; i++)
            if (line[i] == 1)
                cats.push(categories[i - 1])
        filesWithCategories.set(file, cats)
    })

    // Read the identities data file and create the identities array
    const identityData = fs.readFileSync('identity_CelebA.txt').toString().split('\n').map(line => line.split(' ').map(word => word.trim()).filter(word => word.length > 0))
    const identities = []
    identityData.forEach(item => {
        if (!identities.includes(item[1]))
            identities.push(item[1])
    })

    // For each identity, get a list of files associated with that identity (and the categories associated with the file using the Map from above) and save it to JSON
    const data = identities.map(identity => {
        const filesForIdentity = []
        for (let i = 0; i < identityData.length; i++) {
            if (identityData[i][1] == identity)
                filesForIdentity.push({ file: identityData[i][0], categories: filesWithCategories.get(identityData[i][0]) })
        }
        return { identity, files: filesForIdentity }
    })
    fs.writeFileSync('data.json', JSON.stringify({ data }, null, '\t'))
}

// STEP 2: If needed, read data.json and modify it to filter out identities with not enough interesting edge cases, and divide the files for each into train and test images
if (!fs.existsSync('final-data.json')) {
    // Read in the previously saved JSON
    const data = JSON.parse(fs.readFileSync('data.json').toString()).data
    // Get rid of all identities with not enough "difficult" images or not enough images overall
    const filteredData = data.filter(item => item.files.filter(file => file.categories.filter(cat => difficultCategories.includes(cat)).length > 0).length >= minDifficultImages && item.files.length >= numTestImages + numTrainImages)
    console.warn(`Warning: ${filteredData.length} of ${data.length} identities have at least ${minDifficultImages} images with "difficult" categories and at least ${numTestImages + numTrainImages} total images. The remaining ${data.length - filteredData.length} identities will be dropped.`)
    // For each identity, sort the remaining files in order of "difficulty", then grab the first few as testing images and the last few as training images
    const finalData = filteredData.map(item => {
        item.files = item.files.sort((a, b) => {
            const testCategoriesALength = a.categories.filter(cat => difficultCategories.includes(cat)).length
            const testCategoriesBLength = b.categories.filter(cat => difficultCategories.includes(cat)).length
            return testCategoriesBLength - testCategoriesALength
        })
        return { identity: item.identity, testingFiles: item.files.slice(0, numTestImages), trainingFiles: item.files.slice(-numTrainImages) }
    })
    fs.writeFileSync('final-data.json', JSON.stringify({ finalData }, null, '\t'))
}

// STEP 3: Use the final-data.json file to move images in the root of the img_celeba directory into their own <identity>/<train/test> subdirectory
// Read in the previously saved JSON
const finalData = JSON.parse(fs.readFileSync('final-data.json').toString()).finalData
let missingFilesCount = 0
// Create the train and test directories if they don't already exist
const testingDir = `img_celeba/test`
const trainingDir = `img_celeba/train`
if (!fs.existsSync(testingDir) || !fs.statSync(testingDir).isDirectory()) fs.mkdirSync(testingDir)
if (!fs.existsSync(trainingDir) || !fs.statSync(trainingDir).isDirectory()) fs.mkdirSync(trainingDir)
// For each identity, create a subdirectory in the testing directory if needed, then move each testing image from the root of img_celeba into it
finalData.forEach(item => {
    const destDir = `${testingDir}/${item.identity}`
    if (!fs.existsSync(destDir) || !fs.statSync(destDir).isDirectory()) fs.mkdirSync(destDir)
    item.testingFiles.forEach(file => {
        const originalPath = `img_celeba/${file.file}`
        const newPath = `${destDir}/${file.file}`
        if (fs.existsSync(originalPath)) fs.renameSync(originalPath, newPath)
        else missingFilesCount++
    })
})
// Then do the same for training images
finalData.forEach(item => {
    const destDir = `${trainingDir}/${item.identity}`
    if (!fs.existsSync(destDir) || !fs.statSync(destDir).isDirectory()) fs.mkdirSync(destDir)
    item.trainingFiles.forEach(file => {
        const originalPath = `img_celeba/${file.file}`
        const newPath = `${destDir}/${file.file}`
        if (fs.existsSync(originalPath)) fs.renameSync(originalPath, newPath)
        else missingFilesCount++
    })
})
// Warn if any expected files were missing
if (missingFilesCount > 0) console.warn(`Warning: ${missingFilesCount} files are missing.`)

// STEP 4: Delete anything left in the img_celeba directory root that is not a directory (these must be the remaining unused images)
fs.readdirSync('img_celeba').forEach(file => {
    if (!fs.statSync(`img_celeba/${file}`).isDirectory()) fs.unlinkSync(`img_celeba/${file}`)
})

console.log(`Finished:
- Dataset has been split into train and test directories.
- Dataset has been further split into subdirectories based on identity.
- Each identity has ${numTrainImages} training images and ${numTestImages} test images.
- Training images have been picked in alphabetical order, and test images have been picked according to difficulty.
- All extra images have been deleted.`)