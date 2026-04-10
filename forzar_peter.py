import main
import time

# Intentamos detectar la función principal de tu script
# Si tu función principal tiene otro nombre, el script te avisará
for i in range(4):
    print(f"\n🔥 [MANUAL] Iniciando generación del vídeo {i+1} de 4...")
    try:
        # Probamos los nombres más comunes de funciones principales
        if hasattr(main, 'run_bot'):
            main.run_bot()
        elif hasattr(main, 'main'):
            main.main()
        elif hasattr(main, 'process_video'):
            main.process_video()
        else:
            print("❌ No encontré la función principal. Lanza 'python main.py' sin el bucle.")
            break
    except Exception as e:
        print(f"⚠️ Error en la generación {i+1}: {e}")
    
    print(f"✅ Vídeo {i+1} finalizado. Esperando 10 segundos para el siguiente...")
    time.sleep(10)

print("\n✨ ¡Misión cumplida! Los 4 vídeos deberían estar en la carpeta output.")
