const JSDOM = require('jsdom').JSDOM

function createDocument() {
  const base = '<!doctype html><meta charset=utf-8>'
  return new JSDOM(base).window
}

function addTemplate(document, tpl) {
  document.querySelector('body').insertAdjacentHTML('afterbegin', tpl)
  return document
}

const tpl = `
  <div class=tags>
    <label for=tag-1>Tags</label>
    <ul class=tags-list></ul>
    <div class=tag-container>
      <input name=tag-new autocomplete=off list=tags-suggestions>
      <button class=add>+</button>
    </div>
    <ul id=tags-suggestions class=inactive></ul>
  </div>
`

window = createDocument()
document = addTemplate(window.document, tpl)

console.log('document', document)

Tags = require(`${__dirname}/../articles-tags.js`)
