# 2021-05-07 09:48:00.140680
python train_classifier.py --experiment_name=exp_val_mask_7/ce_incomp --inpainter_type=dmfa --inpainter_path ../results/inpainting/mnist/incomplete_data/context_encoder_v1/ --dataset mnist --num_epochs=10 --lr=1e-3 --dump_sample_results --render_every 3 --max_benchmark_batches=-1 --mask_train_size=14 --mask_val_size=7 --convar_type naive
