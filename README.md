
<h1>XSSLECTION is a tool that looks for reflection points for Cross Site Scripting from given URLS</h1>


<h2>How to use XSSLECTION</h2>

```
cat urls.txt | python3 xsslection.py
```
<img width="1498" alt="Screenshot 2023-06-23 at 3 35 40 PM" src="https://github.com/imranfactorial/XSSLECTION/assets/134529947/f8001d50-bbe5-4caf-b706-de7fe74fb874">


By default XSSLECTION will ignore `.jpg, .png, .css, .js` and will print out false positive in JSON response.

XSSLECTION has a debug mode as well. To enable the debug mode just use `-v`. 

At last all the result will be saved in `reflected.txt`.
