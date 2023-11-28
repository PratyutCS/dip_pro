require('dotenv').config();
let Express = require('express')
let path = require('path')
let bodyparser=require('body-parser');
const multer = require('multer');
const { spawn } = require('child_process');
var fs = require('fs');

const upload = multer({
    dest: './project_assets/oi/',
    limits: { fileSize: 5 * 1024 * 1024 }, 
    fileFilter: (req, file, cb) => {
      if (file.mimetype === 'image/jpeg' || file.mimetype === 'image/png') {
        cb(null, true);
      } else {
        cb(new Error('Invalid file type. Only jpeg or png files are allowed.'), false);
      }
    },
    storage: multer.diskStorage({
      destination: (req, file, cb) => {
        cb(null, './project_assets/oi/');
      },
      filename: (req, file, cb) => {
        cb(null, file.originalname); 
      },
    }),
  });

let app = new Express()

app.use(bodyparser.urlencoded({extended: true}));
app.use(Express.json());
app.use(Express.static(__dirname + '/public/css'));
app.use(Express.static(__dirname + '/public/img'));
app.use(Express.static(__dirname + '/public/js'));
app.use(Express.static(__dirname + '/project_assets'));

app.set('view engine','ejs');
app.set("views",path.join(__dirname, "./templates/views"))

let htmlfolder = path.join(__dirname, "/public/html");


app.get("/", (req, res) => {
  res.sendFile(path.join(htmlfolder, "index.html"));
})
app.get("/upload", (req, res) => {
  res.sendFile(path.join(htmlfolder, "upload.html"));
})

app.post('/upload', upload.single('file'), (req, res) => {
  const file = req.file;
  try {
    const pythonProcess = spawn('python3', ['./script.py', "./"+file.path, "./project_assets/wi/"+file.filename, "./project_assets/w/w.jpg", "./project_assets/ew/ew"+file.filename]);
    let dat;
    pythonProcess.stdout.on('data', (data) => {
        dat = `${data}`;
        console.log(`Python script output: ${data}`);
    });

    pythonProcess.stderr.on('data', (data) => {
        console.error(`Error in Python script: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        console.log(`Python script exited with code ${code}`);

        //dat = dat.replaceAll(" ","\n");
        //console.log(dat);

        res.render("result",{
          oi : "/oi/"+file.filename,
          wi : "/wi/"+file.filename,
          w : "/w/w.jpg",
          ew : "/ew/ew"+file.filename,
          data : dat,
      });
    });
  } catch (error) {
      console.error('Error running Python script:', error);
      res.status(500).send('Error running Python script.');
  }
});

app.post("/delete", (req, res) => {
  let oi = path.join((__dirname), "/project_assets"+req.body.oi);
  let wi = (__dirname + '/project_assets')+req.body.wi;
  let ew = (__dirname + '/project_assets')+req.body.ew;
  console.log(oi+" "+wi+" "+ew)
  
  if (fs.existsSync(oi)) {
    fs.unlink(oi, function (err) {
      if (err) throw err;
      console.log(oi+' File deleted!');
    });
  } else {
    console.log('file not present')
  }
  
  if (fs.existsSync(wi)) {
    fs.unlink(wi, function (err) {
      if (err) throw err;
      console.log(wi+' File deleted!');
    });
  } else {
    console.log('file not present')
  }
  
  if (fs.existsSync(ew)) {
    fs.unlink(ew, function (err) {
      if (err) throw err;
      console.log(ew+' File deleted!');
    });
  } else {
    console.log('file not present')
  }
  res.redirect("/");
})

app.get("*", (req, res) => {
    res.sendFile(path.join(htmlfolder, "error.html"));
})

const PORT= process.env.PORT || 3000

app.listen(PORT, () => {
    console.log("Server is running at lolz");
})
