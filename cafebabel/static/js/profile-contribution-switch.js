const translationSwitcher = document.querySelector('.translation-switcher')
const articleSwitcher = document.querySelector('.article-switcher')
const articleList = document.querySelector('.article-list')
const translationList = document.querySelector('.translation-list')

translationSwitcher.addEventListener('click', () => {
  translationSwitcher.classList.add('active')
  articleSwitcher.classList.remove('active')
  /*articleList.style.opacity = 0*/
  fadeOut(articleList)
  fadeIn(translationList)
})
articleSwitcher.addEventListener('click', () => {
  translationSwitcher.classList.remove('active')
  articleSwitcher.classList.add('active')
  /*translationList.style.opacity = 0*/
  fadeOut(translationList)
  fadeIn(articleList)
})

/* http://youmightnotneedjquery.com/ */
function fadeIn(element) {
  element.style.opacity = 0
  let last = +new Date()
  const tick = function() {
    element.style.opacity =
      +element.style.opacity + (new Date() - last) / 400 /* fadein duration */
    last = +new Date()
    if (+element.style.opacity < 1) {
      ;(window.requestAnimationFrame && requestAnimationFrame(tick)) || tick()
    }
  }
  tick()
}
function fadeOut(element) {
  element.style.opacity = 1
  let last = +new Date()
  const tick = function() {
    element.style.opacity =
      +element.style.opacity - (new Date() - last) / 400 /* fadeout duration */
    last = +new Date()
    if (+element.style.opacity > 0) {
      ;(window.requestAnimationFrame && requestAnimationFrame(tick)) || tick()
    }
  }
  tick()
}
