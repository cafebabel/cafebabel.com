/* Auto-expand textarea when typing http://jsfiddle.net/hmelenok/WM6Gq/ */
function textAreaAutoResize(element, event, handler) {
  element.addEventListener(event, handler, false)
}

function textAreaResizing() {
  Array.from(document.querySelectorAll('textarea')).forEach(textArea => {
    function resize() {
      textArea.style.height = `${textArea.scrollHeight}px`
    }

    /* 0-timeout to get the already changed text */
    function delayedResize() {
      window.setTimeout(resize, 0)
    }

    textAreaAutoResize(textArea, 'change', resize)
    textAreaAutoResize(textArea, 'cut', delayedResize)
    textAreaAutoResize(textArea, 'paste', delayedResize)
    textAreaAutoResize(textArea, 'drop', delayedResize)
    textAreaAutoResize(textArea, 'keydown', delayedResize)

    resize()
  })
}

textAreaResizing()
