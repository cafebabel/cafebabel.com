/* Add fixed position to markdown helper */
const markdownHelper = document.querySelector('#markdown-helper')
const saveButton = document.querySelector('.article-page-edit .tags + input')

const editPageTextArea = document.querySelector('.textarea.markdowntext')
const viewportHeight = Math.max(
  document.documentElement.clientHeight,
  window.innerHeight || 0
)
const markdownHelperCross = markdownHelper.querySelector('button')

function isElementInViewport(element) {
  const rect = element.getBoundingClientRect()
  return (
    rect.bottom >= 960 /* 960px to exclude footer height */ &&
    rect.right >= 0 &&
    rect.top <=
      (window.innerHeight || document.documentElement.clientHeight) -
        500 /* 500px after textarea enter viewport */ &&
    rect.left <= (window.innerWidth || document.documentElement.clientWidth)
  )
}
window.addEventListener('scroll', () => {
  const editPageTextAreaHeight = editPageTextArea.clientHeight
  if (
    isElementInViewport(editPageTextArea) &&
    editPageTextAreaHeight >= viewportHeight
  ) {
    markdownHelper.classList.add('fixed')
    saveButton.classList.add('fixed')
  } else {
    markdownHelper.classList.remove('fixed')
    saveButton.classList.remove('fixed')
  }
})
markdownHelperCross.addEventListener('click', event => {
  event.preventDefault()
  markdownHelper.classList.add('close')
})
