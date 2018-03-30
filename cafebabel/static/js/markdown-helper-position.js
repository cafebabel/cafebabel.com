/* Add fixed position to markdown helper */
const markdownHelper = document.querySelector('#markdown-helper')

const editPageTextArea = document.querySelector('.textarea.bodytext'),
  editPageTextAreaHeight = editPageTextArea.offsetHeight,
  viewportHeight = Math.max(
    document.documentElement.clientHeight,
    window.innerHeight || 0
  ),
  markdownHelperCross = markdownHelper.querySelector('button')

function isElementInViewport(el) {
  const rect = el.getBoundingClientRect()
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
  if (
    isElementInViewport(editPageTextArea) &&
    editPageTextAreaHeight >= viewportHeight
  ) {
    markdownHelper.classList.add('fixed')
  } else {
    markdownHelper.classList.remove('fixed')
  }
})
markdownHelperCross.addEventListener('click', event => {
  event.preventDefault()
  markdownHelper.classList.remove('fixed')
})
