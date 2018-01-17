class Tags {
  constructor() {
    const context = document.querySelector('.tags')
    this.list = context.querySelector('.tags-list')
    this.buttonAdd = context.querySelector('input[name=tag-new]')
    this.suggestions = context.querySelector('#tags-suggestions')
    this.values = Array.from(this.list.querySelectorAll('input')).map(
      input => input.value
    )
  }
  static addNewTag(submission) {
    const tags = new Tags()
    if (!submission || tags._isTag(submission)) return
    tags._addValue(submission)
    tags._emptyAddField()
    tags._inactiveSuggestionsList()
    tags._render()
    TagEffect.fadeIn(tags.list.querySelector('li:last-child'))
  }
  static removeTag(tagElement) {
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
  _emptyAddField() {
    this.buttonAdd.value = ''
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
    const tagButtonAdd = document.querySelector('.tags button.add')
    tagButtonAdd.addEventListener('click', event => {
      event.preventDefault()
      const submission = event.target.previousSibling.value
      Tags.addNewTag(submission)
    })
  }
  static addRemoveListener() {
    const tagsButtonRemove = document.querySelectorAll('.tags-list li button')
    tagsButtonRemove.forEach(button =>
      button.addEventListener('click', event => {
        event.preventDefault()
        const tagElement = event.target.parentNode
        Tags.removeTag(tagElement)
      })
    )
  }
  static keyup() {
    function handleSuggestion(tag) {
      const tagsSuggestion = document.querySelector('#tags-suggestions')
      tagsSuggestion.innerHTML = ''
      const li = document.createElement('li')
      li.append(tag.name)
      tagsSuggestion.appendChild(li)
      tagsSuggestion.classList.remove('inactive')
      tagsSuggestion.addEventListener('click', event => {
        const submission = event.target.innerText
        Tags.addNewTag(submission)
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
      const languages = document.querySelector('#language')
      const language = languages.options[languages.selectedIndex].value
      if (submission.length < 3) return
      request(`/article/tag/suggest/?language=${language}&terms=${submission}`)
        .then(response => response.forEach(handleSuggestion))
        .catch(console.error.bind(console))
    })
  }
}

TagEventListener.clickAdd()
TagEventListener.keyup()

window.addEventListener('load', () => TagEventListener.addRemoveListener())
