var express = require('express');
var app = express();
var swaggerUi = require('../../index');
var swaggerDocument = require('./swagger.json');

var swaggerDocumentSplit = require('./swagger-split.json');

app.use((req, res, next) => {
	if (req.url === '/favicon.ico') {
		res.sendFile(__dirname + '/favicon.ico');
	} else if (req.url === '/swagger.json') {
		res.sendFile(__dirname + '/swagger.json');
	} else if (req.url === '/my-custom.css') {
		res.sendFile(__dirname + '/my-custom.css');
	} else {
		next();
	}
});

var options = {
	preauthorizeApiKey: {
	 authDefinitionKey: 'api_key',
	 apiKeyValue: 'Bearer XYZ'
	},
	validatorUrl : null,
	oauth: {
	 clientId: "your-client-id1",
	 clientSecret: "your-client-secret-if-required1",
	 realm: "your-realms1",
	 appName: "your-app-name1",
	 scopeSeparator: ",",
	 additionalQueryStringParams: {}
 },
 docExpansion: 'full',
 operationsSorter: function (a, b) {
	 var score = {
		 '/test': 1,
		 '/bar': 2
	 }
	 console.log('a', a.get("path"), b.get("path"))
	 return score[a.get("path")] < score[b.get("path")]
 }
};
app.get('/examples', function (req,res){
	const urls = []
	for (register of (app._router.stack)){
		register.route?.path?urls.push(register.route.path):''
	}
	res.json({urls});
})
app.post('/test', function(req, res) {
	console.log('req', req)
	res.json({ status: 'OK'});
});
app.get('/bar', function(req, res) { res.json({ status: 'OKISH'}); });

app.use('/api-docs', swaggerUi.serve)
app.get('/api-docs', swaggerUi.setup(swaggerDocument, false, options, '.swagger-ui .topbar { background-color: red }'));

app.use('/api-docs-one', swaggerUi.serve, swaggerUi.setup(swaggerDocument, false, options, '.swagger-ui .topbar { background-color: red }'))

app.use('/api-docs-from-url', swaggerUi.serve)
app.get('/api-docs-from-url', swaggerUi.setup(null, false, options, '.swagger-ui .topbar { background-color: red }', null, '/swagger.json'));

var swaggerUiOpts = {
	explorer: false,
	swaggerOptions: options,
	customCss: '.swagger-ui .topbar { background-color: blue }'
}

app.use('/api-docs-using-object', swaggerUi.serve)
app.get('/api-docs-using-object', swaggerUi.setup(swaggerDocument, swaggerUiOpts));

var swaggerUiOpts2 = {
	explorer: false,
	swaggerOptions: options,
	customCss: '.swagger-ui .topbar { background-color: pink }',
	swaggerUrl: '/swagger.json',
	customJs: '/my-custom.js',
	operationsSorter: 'alpha',
	customCssUrl: 'https://cdn.jsdelivr.net/npm/swagger-ui-themes@3.0.0/themes/3.x/theme-newspaper.css'
}

app.use('/api-docs-from-url-using-object', swaggerUi.serve)
app.get('/api-docs-from-url-using-object', swaggerUi.setup(null, swaggerUiOpts2));

app.use('/api-docs-from-css-url', swaggerUi.serve)
app.get('/api-docs-from-css-url', swaggerUi.setup(null, swaggerUiOpts2));

app.use('/api-docs-with-null', swaggerUi.serve)
app.get('/api-docs-with-null', swaggerUi.setup(swaggerDocument, null, options, '.swagger-ui .topbar { background-color: orange }'));

app.use('/api-docs-split', swaggerUi.serve)
app.get('/api-docs-split', swaggerUi.setup(swaggerDocumentSplit, null, options, '.swagger-ui .topbar { background-color: orange }'));

app.use('/api-docs-with-opts/', swaggerUi.serveWithOptions({ redirect: false, cacheControl: false }))
app.get('/api-docs-with-opts/', swaggerUi.setup(swaggerDocumentSplit, null, options, '.swagger-ui .topbar { background-color: orange }'));

var swaggerHtml = swaggerUi.generateHTML(swaggerDocument, swaggerUiOpts)

app.use('/api-docs-html1', swaggerUi.serveFiles(swaggerDocument, swaggerUiOpts))
app.get('/api-docs-html1', (req, res) => { res.send(swaggerHtml) });

let count = 0
app.use('/api-docs-dynamic', function(req, res, next){
    count = count + 1
    swaggerDocument.info.description = `Hello ${count}!`;
    req.swaggerDoc = swaggerDocument;
    next();
}, swaggerUi.serveFiles(), swaggerUi.setup());

var swaggerUiOpts3 = {
	explorer: false,
	swaggerOptions: options,
	customCss: '.swagger-ui .topbar { background-color: pink }',
	swaggerUrl: '/swagger.json',
	customJsStr: 'window.alert("123")',
	operationsSorter: 'alpha',
}

app.use('/api-docs-jsstr', swaggerUi.serve)
app.get('/api-docs-jsstr', swaggerUi.setup(null, swaggerUiOpts3));

var swaggerUiOpts4 = {
	swaggerOptions: {
		url: 'http://localhost:' + (app.get('port') || 3001) + '/swagger.json'
	}
}

app.use('/api-docs-with-url-in-swaggerOptions', swaggerUi.serve)
app.get('/api-docs-with-url-in-swaggerOptions', swaggerUi.setup(null, swaggerUiOpts4));


var swaggerUiOpts5 = {
	swaggerOptions: {
		url: 'http://localhost:' + (app.get('port') || 3001) + '/swagger.json',
		preauthorizeApiKey: {
			authDefinitionKey: 'api_key',
			apiKeyValue: 'Bearer XYZ'
		   }
	}
}

app.use('/api-docs-with-url-in-swaggerOptions-preauthorized', swaggerUi.serve)
app.get('/api-docs-with-url-in-swaggerOptions-preauthorized', swaggerUi.setup(null, swaggerUiOpts5));


app.use(function(req, res) {
    res.status(404).send('Page not found');
});

module.exports = app;
