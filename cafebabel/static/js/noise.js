/* tv noise effect https://codepen.io/eugene-bulkin/pen/zEgyH */
const canvas = document.querySelector('.noise')
if (canvas) {
  const context = canvas.getContext('2d')

  function resize() {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.onresize = resize

  function noise(context) {
    const w = context.canvas.width
    const h = context.canvas.height
    const idata = context.createImageData(w, h)
    const buffer32 = new Uint32Array(idata.data.buffer)
    const len = buffer32.length
    for (let i = 0; i < len; ) buffer32[i++] = ((50 * Math.random()) | 0) << 24
    context.putImageData(idata, 0, 0)
  }
  let toggle = true
  ;(function loop() {
    toggle = !toggle
    if (toggle) {
      requestAnimationFrame(loop)
      return
    }
    noise(context)
    requestAnimationFrame(loop)
  })()
}
