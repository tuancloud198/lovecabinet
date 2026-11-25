// The dog pet: a body per growth stage (no head) + a head per mood, put together by PetArt.vue.
import body1 from './body-1.webp'
import body2 from './body-2.webp'
import body3 from './body-3.webp'
import neutral from './head-neutral.webp'
import happy from './head-happy.webp'
import shy from './head-shy.webp'
import excited from './head-excited.webp'
export default {
  bodies: [body1, body2, body3],
  heads: { neutral, happy, shy, excited },
  // Where the head goes on each body, as % of the body image: x/y = top-left of the head image, w = its width
  // (height follows the head's aspect ratio), r = rotation in degrees around the head's centre.
  anchors: [{ x: 26.25, y: 11.47, w: 73.02, r: -1.5 }, { x: 19.9, y: -1.74, w: 80.5, r: -4.2 }, { x: 8.22, y: -1.97, w: 84.31, r: -4.4 }],
  // Image sizes (viewBox width/height), so PetArt can lay both out in one SVG.
  bodySizes: [[337, 232], [370, 287], [480, 401]],
  headSize: [317, 254],
}
