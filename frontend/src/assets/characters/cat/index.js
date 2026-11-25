// The cat pet: a body per growth stage (no head) + a head per mood, put together by PetArt.vue.
import body1 from './body-1.svg'
import body2 from './body-2.svg'
import body3 from './body-3.svg'
import neutral from './head-neutral.svg'
import happy from './head-happy.svg'
import shy from './head-shy.svg'
import excited from './head-excited.svg'
export default {
  bodies: [body1, body2, body3],
  heads: { neutral, happy, shy, excited },
  // Where the head goes on each body, as % of the body image: x/y = top-left of the head image, w = its width
  // (height follows the head's aspect ratio), r = rotation in degrees around the head's centre.
  anchors: [{ x: 7.43, y: 0.65, w: 77.72, r: 0 }, { x: 4.63, y: 0.51, w: 69.78, r: 0 }, { x: 9.25, y: 2.99, w: 61.34, r: 0 }],
  // Image sizes (viewBox width/height), so PetArt can lay both out in one SVG.
  bodySizes: [[404, 308], [396, 358], [430, 372]],
  headSize: [314, 226],
}
