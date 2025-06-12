import Swal from "sweetalert2";

export function initProductMain() {
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

const productForm = document.getElementById("product_form") as HTMLFormElement;

function cancelFormSubmit(productForm: HTMLFormElement): void {
  productForm.addEventListener("keydown", (e: KeyboardEvent) => {
    const target = e.target as HTMLInputElement;
    if (e.key === "Enter" && target.tagName !== "TEXTAREA") {
      e.preventDefault();
    }
  });
}

function saveForm(productForm: HTMLFormElement): void {
  document.addEventListener("keydown", (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "s") {
      // Override the default browser behavior, which is save the page.
      e.preventDefault();
      productForm.submit();
    }
  });
}

function deleteProduct(productForm: HTMLFormElement): void {
  const deleteButtons = document.querySelectorAll<HTMLButtonElement>('[type="button"]');
  for (const deleteButton of deleteButtons) {
    deleteButton.addEventListener("click", () => {
      const deleteCheckbox = deleteButton.closest(".text-center")?.querySelector('[name$="DELETE"]') as HTMLInputElement;

      if (!deleteCheckbox) {
        return;
      }

      Swal.fire({
        text: "本当にこの商品を削除しますか？",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: "rgb(220, 38, 38)",
        cancelButtonColor: "rgb(37, 99, 235)",
        confirmButtonText: "削除",
        cancelButtonText: "キャンセル"
      }).then(result => {
        if (result.isConfirmed) {
          deleteCheckbox.checked = true;
          productForm.submit();
        }
      });
    });
  }
}

const brandMappings = {
  "え": "エルメス",
  "しゃ": "シャネル",
  "べ": "ベルルッティ",
  "せ": "セリーヌ",
};

const productNameMappings = {
  "ぴこ": "ピコタンロック",
  "がー": "ガーデンパーティ",
  "じっぴ": "ジッピーウォレット",
  "みゅ": "ミュルティクレ",
};

const materialColorMappings = {
  "とり": "トリヨンクレマンス",
};

function autocompleteInput(selector: string, mappings: Record<string, string>): void {
  const inputs = document.querySelectorAll<HTMLInputElement>(selector);
  for (const input of inputs) {
    input.addEventListener("input", (e: Event) => {
      const target = e.target as HTMLInputElement;
      const value = target.value;
      if (value && mappings[value]) {
        target.value = mappings[value];
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
