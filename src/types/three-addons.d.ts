/**
 * Type declarations for three/addons modules.
 * Resolves ts(7016) for imports from "three/addons/loaders/GLTFLoader.js"
 * and other three/addons subpaths.
 */
declare module "three/addons/loaders/GLTFLoader.js" {
  export { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader.js";
}

declare module "three/addons/*" {
  const value: any;
  export default value;
  export = value;
}
