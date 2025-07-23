declare global {
  interface Window {
    pywebview: {
      api: {
        echo: (message: string) => Promise<string>;
        perform_ocr: (
          imagePath: string
        ) => Promise<{ success: boolean; text?: string; error?: string }>;
        save_file: (
          content: string,
          filename: string
        ) => Promise<{ success: boolean; message?: string; error?: string }>;
        get_system_info: () => Promise<{
          platform: string;
          version: string;
          machine: string;
        }>;
        scan_qrcode: (image: string) => Promise<{
          success: boolean;
          content?: {
            fixed_value?: string;
            invoice_type?: string;
            invoice_code?: number;
            invoice_number?: string;
            amount?: string;
            date?: string;
            check_code?: string;
            encrypt?: string;
          };
          error?: string;
        }>;
        img_ocr: (image: string) => Promise<{
          success: boolean;
          content?: {
            date: string;
            program: string;
            amount: string;
            content: string;
            invoice_number: number;
          };
          error?: string;
        }>;
      };
    };
  }
}
