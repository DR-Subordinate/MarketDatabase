import {
  cancelFormSubmit,
  saveForm,
  deleteProduct,
  brandMappings,
  productNameMappings,
  materialColorMappings,
  autocompleteInput
} from "../common/form_utils";

export function initProductMain() {
  const productForm = document.getElementById("product_form") as HTMLFormElement;

  formatPrice();
  toggleSaveProduct();
  cancelFormSubmit(productForm);
  saveForm(productForm);
  deleteProduct(productForm);
  autocompleteInput('input[name$="brand_name"]', brandMappings);
  autocompleteInput('input[name$="-name"]', productNameMappings);
  autocompleteInput('input[name$="material_color"]', materialColorMappings);
}

function formatPrice(): void {
  const priceInputs = document.querySelectorAll<HTMLInputElement>('input[name$="price"], input[name$="winning_bid"]');

  for (const priceInput of priceInputs) {
    priceInput.addEventListener("blur", (e: Event) => {
      const target = e.target as HTMLInputElement;
      const value = target.value;
      if (value) {
        const cleanValue = value.replace(/,/g, "");
        const numericValue = Number(cleanValue);
        const formattedValue = numericValue.toLocaleString();
        target.value = formattedValue;
      }
    });
  }
}

interface ToggleElements {
  saveProductHeader: HTMLElement;
  saveProductHeaderText: HTMLElement;
  saveProductTable: HTMLElement;
}

function getToggleElements(): ToggleElements | null {
  const saveProductHeader = document.getElementById("save_product_header");
  const saveProductHeaderText = document.querySelector<HTMLElement>("#save_product_header > .text-blue-500");
  const saveProductTable = document.getElementById("save_product_container");

  if (!saveProductHeader || !saveProductHeaderText || !saveProductTable) {
    return null;
  }

  return { saveProductHeader, saveProductHeaderText, saveProductTable };
}

function toggleSaveProduct(): void {
  const toggleElements = getToggleElements();

  if (!toggleElements) {
    return;
  }

  toggleElements.saveProductHeader.addEventListener("click", () => {
    const isHidden = toggleElements.saveProductTable.classList.toggle("hidden");
    toggleElements.saveProductHeaderText.textContent = isHidden ? "+" : "−";
  });
}
