# 2021-05-17 10:26:56.276954
python train_classifier.py --experiment_name=tryout/mfa_frozen --inpainter_type=mfa --inpainter_path ../../gmm_missing/models/svhn_32_32/ --dataset svhn --img_size 32 --mask_train_size 0 --mask_unknown_size 16 --mask_val_size 16 --num_epochs=25 --lr=1e-3 --dump_sample_results --render_every 3 --dataset_root /mnt/remote/wmii_gmum_projects/datasets/vision/SVHN/ --max_benchmark_batches=-1
