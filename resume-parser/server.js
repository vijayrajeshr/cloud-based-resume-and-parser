const express = require('express');
const multer = require('multer');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs').promises;

const app = express();
const port = 3000;

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: async (req, file, cb) => {
        const uploadDir = path.join(__dirname, 'uploads');
        await fs.mkdir(uploadDir, { recursive: true });
        cb(null, uploadDir);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });

app.use(express.static('public'));
app.use(express.json()); // To parse JSON request bodies

app.post('/upload', upload.single('resume'), async (req, res) => {
    if (!req.file) {
        return res.status(400).send('No file uploaded.');
    }

    const filePath = req.file.path;

    try {
        const pythonProcess = spawn('python', ['parser.py', filePath]);
        let parsedData = '';
        let errorData = '';

        pythonProcess.stdout.on('data', (data) => {
            parsedData += data.toString();
        });

        pythonProcess.stderr.on('data', (data) => {
            errorData += data.toString();
        });

        pythonProcess.on('close', (code) => {
            // Clean up the uploaded file
            fs.unlink(filePath).catch(err => console.error('Error deleting file:', err));

            if (code === 0) {
                try {
                    const jsonData = JSON.parse(parsedData);
                    res.json(jsonData);
                } catch (parseError) {
                    console.error('Error parsing JSON:', parseError);
                    console.error('Raw output from parser:', parsedData);
                    res.status(500).send('Error processing parsed data.');
                }
            } else {
                console.error('Parser script failed with code', code);
                console.error('Stderr:', errorData);
                res.status(500).send(`Resume parsing failed. Error: ${errorData}`);
            }
        });
    } catch (error) {
        console.error('Error spawning parser:', error);
        res.status(500).send('Internal server error.');
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});