class Tags {
  constructor() {
    const context = document.querySelector('.tags')
    this.list = context.querySelector('.tags-list')
    this.fieldAdd = context.querySelector('input[name=tag-new]')
    this.buttonAdd = context.querySelector('button.add')
    this.removeButtons = context.querySelectorAll('.tags-list li button')
    this.suggestions = context.querySelector('#tags-suggestions')
    this.values = Array.from(this.list.querySelectorAll('input')).map(
      input => input.value
    )
  }
  addNewTag(submission) {
    const tags = new Tags()
    if (!submission || tags._isTag(submission)) return
    tags._addValue(submission)
    tags._emptyAddField()
    tags._inactiveSuggestionsList()
    tags._render()
    TagEffect.fadeIn(tags.list.querySelector('li:last-child'))
  }
  removeTag(tagElement) {
    const submission = tagElement.innerText
    const tags = new Tags()
    if (tags._isTag(submission)) {
      tags._removeValue(submission)
      TagEffect.fadeOut(tagElement).then(tags._render)
      tags._render()
    }
  }
  _isTag(tag) {
    return this.values.includes(tag)
  }
  _addValue(query) {
    this.values = this.values.concat(query)
  }
  _removeValue(query) {
    this.values = this.values.filter(value => value !== query)
  }
  _createTagsList(container, tagValues) {
    tagValues.forEach((tagValue, index) =>
      container.insertAdjacentHTML(
        'beforeend',
        this._createTag(tagValue, index)
      )
    )

    return container
  }
  _createTag(tagValue, index) {
    return `
      <li>
        ${tagValue}
        <input name="tag-${++index}" list="tags" value=${tagValue} type="hidden">
        <button></button>
      </li>
    `
  }
  _inactiveSuggestionsList() {
    this.suggestions.classList.add('inactive')
  }
  _activeSuggestionsList() {
    this.suggestions.classList.remove('inactive')
  }
  _emptyAddField() {
    this.fieldAdd.value = ''
  }
  _render() {
    const container = this.list.cloneNode(false)
    this.list.replaceWith(this._createTagsList(container, this.values))
    TagEventListener.addRemoveListener()
  }
}

class TagEffect {
  static fadeIn(element) {
    function fade() {
      element.style.opacity = +element.style.opacity + 0.03
      if (element.style.opacity <= 1) {
        requestAnimationFrame(fade)
      }
    }
    console.log('TOC FADE')
    element.style.opacity = 0
    fade()
  }
  static fadeOut(element) {
    function fade() {
      element.style.opacity = +element.style.opacity - 0.03
      if (element.style.opacity < 0) {
        element.style.display = 'none'
        resolve()
      } else {
        requestAnimationFrame(fade)
      }
    }

    element.style.opacity = 1

    return new Promise((resolve, reject) => fade())
  }
}

class TagEventListener {
  static clickAdd() {
    const tags = new Tags()
    tags.buttonAdd.addEventListener('click', event => {
      event.preventDefault()
      const submission = event.target.previousSibling.value
      tags.addNewTag(submission)
    })
  }
  static addRemoveListener() {
    const tags = new Tags()
    tags.removeButtons.forEach(button =>
      button.addEventListener('click', event => {
        event.preventDefault()
        const tagElement = event.target.parentNode
        tags.removeTag(tagElement)
      })
    )
  }
  static keyup() {
    function handleSuggestion(submission) {
      const tags = new Tags()
      tags._activeSuggestionsList()
      const li = `<li>${submission.name}</li>`
      tags.suggestions.insertAdjacentHTML('beforeend', li)
      tags.suggestions.addEventListener('click', event => {
        const submission = event.target.innerText
        tags.addNewTag(submission)
      })
    }

    const inputNewTag = document.querySelector('.tags input[name=tag-new]')
    inputNewTag.addEventListener('keypress', event => {
      /* Return if arrow up, arrow down or enter are pressed */
      if (event.keyCode == 13) {
        return
      }
      if (event.keyCode == 40 || event.keyCode == 38) return
      const submission = event.target.value
      if (submission.length < 2) return
      request(`/article/tag/suggest/?language=en&terms=${submission}`)
        .then(response => response.forEach(handleSuggestion))
        .catch(console.error.bind(console))
    })
  }
}

TagEventListener.clickAdd()
TagEventListener.keyup()

window.addEventListener('load', () => TagEventListener.addRemoveListener())
