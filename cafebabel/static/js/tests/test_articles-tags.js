/**
 * Unit-Tests for articles-tags.js
 *
 * We have to exchange with team about the test stack.
 * This implementation is a minimal config without any installation on the repository.
 * To play with tests, you have to install : jsdom, chai and mocha.
 * With npm you can complete with : npm link pour jsdom, chai and mocha.
 * Then $ mocha static/js/tests/test_articles-tags.js
 */

const expect = require('chai').expect
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

describe('Tags', () => {
  const tags = new Tags.Tags()

  it('should retrieve -input- whose add tag', () => {
    const field = tags.fieldAdd
    expect(field.localName).to.equal('input')
  })
})
