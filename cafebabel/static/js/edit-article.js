class Tags {
  constructor(domContext) {
    this.list = domContext.querySelector('ul')
    this.values = Array.from(this.list.querySelectorAll('li')).map(li => li.innerText)
    this.submission = domContext.querySelector('input[name=tag-new]').value
  }
  checkSubmission() {
    return this.submission && ! this._isTag(this.submission)
  }
  display() {
    const tagsValue = this.values.concat(this.submission)
    const container = this.list.cloneNode(false)
    this.list.replaceWith(this._createTagsList(container, tagsValue))
  }

  _isTag(tag) {
    return this.values.includes(tag)
  }
  _createTagsList(container, tagValues) {
    tagValues.forEach((tagValue, index) => container.appendChild(this._createTag(tagValue, index)))

    return container
  }
  _createTag(tagValue, index) {
    const li = document.createElement('li')
    const input = document.createElement('input')
    input.type = 'hidden'
    input.name = `tag-${index + 1}`
    input.setAttribute('list', 'tags')
    input.value = tagValue
    li.append(tagValue)
    li.append(input)

    return li
  }
}


const tagButtonAdd = document.querySelector('.tags button.add')
const tagButtonRemove = document.querySelector('.tags button.remove')

tagButtonAdd.addEventListener('click', (event) => {
  event.preventDefault()
  const tags = new Tags(document.querySelector('.tags'))
  if (!tags.checkSubmission()) return
  tags.display()
})

