/**
 * Unit-Tests for articles-tags.js
 *
 * We have to exchange with team about the test stack.
 * This implementation is a minimal config without any installation on the repository.
 * To play with tests, you have to install : jsdom, chai and mocha.
 * With npm you can complete with : npm link pour jsdom, chai and mocha.
 * Then :
 * $ mocha static/js/tests/test_articles-tags.js
 */

const expect = require('chai').expect
const JSDOM = require('jsdom').JSDOM

window = {}
document = {}

class MockDocument {
  constructor(tpl) {
    this.base = '<!doctype html><meta charset=utf-8>'
    this._initDom()
  }
  get outerHTML() {
    console.info('info > html document:', this.dom.serialize())
  }
  reset() {
    this._initDom()
    return this._initTags()
  }
  _initDom() {
    window = new JSDOM(this.base, { pretendToBeVisual: true }).window
    document = window.document
    this._injectTpl(tpl)
  }
  _initTags() {
    const tags = new Tags.Tags()

    // mock _request, we don't want test XHR
    tags._request = submission => {
      return new Promise(resolve => {
        // like 'Joseki' is already saved
        if (submission === 'Joseki') {
          resolve([
            { language: 'en', name: submission, slug: submission, summary: '' }
          ])
        } else {
          resolve([])
        }
      })
    }
    return tags
  }
  _injectTpl(tpl) {
    const body = document.querySelector('body')
    body.innerHTML = ''
    document.querySelector('body').insertAdjacentHTML('beforeend', tpl)
  }
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
      <li class=saved>Joseki<input name=tag-1 list=tags value=Joseki type=hidden>
        <button type=button></button>
      </li><li class=saved>Fuseki<input name=tag-2 list=tags value=Fuseki type=hidden>
        <button type=button></button>
      </li>
    </ul>
    <div class=tag-container><input name=tag-new autocomplete=off list=tags-suggestions><button class=add>+</button></div>
    <ul id=tags-suggestions class=inactive></ul>
  </div>
`

const mock = new MockDocument(tpl)

// need -document- before import
const Tags = require(`${__dirname}/../articles-tags.js`)

describe('Tags', () => {
  describe('Find', () => {
    it('should retrieve -input- whose add tag', () => {
      const tags = mock.reset()
      const field = tags.fieldAdd
      expect(field.localName).to.equal('input')
    })
    it('should get language', () => {
      const tags = mock.reset()
      expect(tags._language).to.equal('en')
    })
    it('should verify when a tag is in a current list', () => {
      const tags = mock.reset()
      expect(tags._isTagName('Joseki')).to.be.true
    })
    it('should verify if a tag is not in a current list', () => {
      const tags = mock.reset()
      expect(tags._isTagName('ChessMate')).to.be.false
    })
  })

  describe('Render', () => {
    it("should render a tag's list", () => {
      const tags = mock.reset()
      tags._render(['Burial', 'Jlin', 'Arca', 'Bibio']).then(() => {
        expect(tags._tagsNames.length).to.equal(4)
      })
    })
  })

  describe('Remove', () => {
    it("should retrieve the tag's value", () => {
      const tags = mock.reset()
      expect(tags._tagsNames.length).to.equal(2)
    })
    it('should do nothing when name is inexistant', () => {
      const tags = mock.reset()
      expect(tags.removeTag('chessmate')).to.equal(undefined)
      expect(tags._tagsNames.length).to.equal(2)
    })
    it('should remove the tag', () => {
      const tags = mock.reset()
      tags
        .removeTag('Fuseki')
        .then(() => expect(tags._tagsNames.length).to.equal(1))
    })
  })

  describe('Add', () => {
    it('should add new tag to the current list', () => {
      const tags = mock.reset()
      expect(tags._tagsNamesAdd('Tesuji')).to.contains('Tesuji')
    })
    it('should add new tag', () => {
      const tags = mock.reset()
      tags
        .addNewTag('Keima')
        .then(() => expect(tags._tagsNames).to.contains('Keima'))
    })
    it('should change nothing when new tag exists', () => {
      const tags = mock.reset()
      tags.addNewTag('Joseki')
      expect(tags.addNewTag('Joseki')).to.equal(undefined)
      expect(tags._tagsNames.length).to.equal(2)
    })
  })

  describe('Submission', () => {
    it('should verify that a tag is previously saved', () => {
      const tags = mock.reset()
      tags._isTagSaved('Joseki').then(response => expect(response).to.be.true)
    })
    it('should verify that a tag is not previously saved', () => {
      const tags = mock.reset()
      tags._isTagSaved('Akira').then(response => expect(response).to.be.false)
    })
  })
})
