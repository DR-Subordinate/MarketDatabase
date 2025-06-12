import {
  cancelFormSubmit,
  saveForm,
  deleteProduct,
  brandMappings,
  productNameMappings,
  materialColorMappings,
  autocompleteInput
} from "../common/form_utils";

export function initProductRegister() {
  const productForm = document.getElementById("product_form") as HTMLFormElement;

  cancelFormSubmit(productForm);
  saveForm(productForm);
  deleteProduct(productForm);
  autocompleteInput('input[name$="brand_name"]', brandMappings);
  autocompleteInput('input[name$="-name"]', productNameMappings);
  autocompleteInput('input[name$="material_color"]', materialColorMappings);
}
