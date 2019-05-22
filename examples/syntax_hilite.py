import streamlit as st
from collections import namedtuple

Language = namedtuple('Language', ['name', 'example'])

languages = [
    Language(name='Python',
             example="""
# Python
def say_hello():
    name = 'Streamlit'
    print('Hello, %s!' % name)"""),

    Language(name='C',
             example="""
/* C */
int main(void) {
    const char *name = "Streamlit";
    printf(\"Hello, %s!\", name);
    return 0;
}"""),

    Language(name='Javascript',
             example="""
// Javascript
function sayHello() {
    const name = 'Streamlit';
    console.log(`Hello, ${name}!`);
}"""),

    Language(name='Shell',
             example="""
# Bash/Shell
NAME="Streamlit"
echo "Hello, ${NAME}!"
"""),

    Language(name='SQL',
             example="""
/* SQL */
SELECT * FROM software WHERE name = 'Streamlit';
"""),

    Language(name='JSON',
             example="""

{
    "_comment": "This is a JSON file!",
    name: "Streamlit",
    version: 0.27
}"""),

    Language(name='YAML',
             example="""
# YAML
software:
    name: Streamlit
    version: 0.27
"""),

    Language(name='HTML',
             example="""
<!-- HTML -->
<head>
  <title>Hello, Streamlit!</title>
</head>
"""),

    Language(name='CSS',
             example="""
/* CSS */
.style .token.string {
    color: #9a6e3a;
    background: hsla(0, 0%, 100%, .5);
}
"""),
]


st.header('Syntax hiliting')

st.subheader('Languages')
for lang in languages:
    st.code(lang.example, lang.name)

st.subheader('Other stuff')
with st.echo():
    print("I'm inside an st.echo() block!")

st.markdown("""
This is a _markdown_ block...
```python
print('...and syntax hiliting works here, too')
```
""")

