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
  document.querySelector('body').insertAdjacentHTML('beforeend', tpl)
  return document
}

const tpl = `
  <select id=language>
    <optgroup label=Language>
      <option value=fr>Italie</option>
      <option value=en selected=>English</option>
      <option value=fr>Français</option>
    </optgroup>
  </select>
  <div class=tags>
    <label for=tag-1>Tags</label>
    <ul class=tags-list>
      <li class=saved>Joseki
        <input name=tag-1 list=tags value=Joseki type=hidden>
        <button type=button></button>
      </li>
      <li>Tesuji
        <input name=tag-2 list=tags value=Tesuji type=hidden>
        <button type=button></button>
      </li>
    </ul>
    <div class=tag-container>
      <input name=tag-new autocomplete=off list=tags-suggestions>
      <button class=add>+</button>
    </div>
    <ul id=tags-suggestions class=inactive></ul>
  </div>
`

window = createDocument()
document = addTemplate(window.document, tpl)

Tags = require(`${__dirname}/../articles-tags.js`)

describe('Tags', () => {
  const tags = new Tags.Tags()

  it('should retrieve -input- whose add tag', () => {
    const field = tags.fieldAdd
    expect(field.localName).to.equal('input')
  })
  it('should get language', () => {
    expect(tags._language).to.equal('en')
  })
})
