import Swal from "sweetalert2";

export function initProductRegister() {
  cancelFormSubmit(productForm);
  saveForm(productForm);
  deleteProduct(productForm);
  autocompleteInput('input[name$="brand_name"]', brandMappings);
  autocompleteInput('input[name$="-name"]', productNameMappings);
  autocompleteInput('input[name$="material_color"]', materialColorMappings);
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
