# 2021-05-16 23:26:52.234054
python train_classifier_v2.py --experiment_name=tryout/mfa_frozen_cnv --inpainter_type=mfa --inpainter_path ../../gmm_missing/models/cifar10_32_32/ --dataset cifar10 --img_size 32 --mask_train_size 0 --mask_unknown_size 16 --mask_val_size 16 --num_epochs=25 --lr=1e-4 --dump_sample_results --render_every 3 --max_benchmark_batches=-1 --cls_bl 3 --cls_latent_size 256 --cls_dropout=0.5 --cls_depth 3 --convar_type naive
