import os
from rembg import remove
from PIL import Image

# 1. Defina os caminhos das pastas
input_folder = '../dataset/rick_owens_boots'
output_folder = '../dataset/rick_owens_boots_no_background'

# 2. Garante que a pasta de saída exista
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 3. Processa cada imagem da pasta de entrada
for filename in os.listdir(input_folder):
    # Verifica se o arquivo é uma imagem válida
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        input_path = os.path.join(input_folder, filename)
        
        # Como o fundo será removido (transparente), a saída DEVE ser .png
        output_filename = os.path.splitext(filename)[0] + '.png'
        output_path = os.path.join(output_folder, output_filename)

        print(f"Processando: {filename}...")
        
        try:
            # Carrega a imagem original com o Pillow
            input_image = Image.open(input_path)
            
            # Aplica a rede neural do rembg para remover o fundo
            output_image = remove(input_image)
            
            # Salva a nova imagem isolada
            output_image.save(output_path, 'PNG')
            print(f"Sucesso! Salvo como {output_filename}")
            
        except Exception as e:
            print(f"Erro ao processar {filename}: {e}")

print("\nProcessamento concluído!")