# 2021-05-20 02:39:15.143467
python train_classifier_v2.py --experiment_name=tryout_dropout/inp_zero --convar_type=naive --inpainter_type=zero --dataset cifar10 --img_size 32 --mask_train_size 0 --mask_unknown_size 16 --mask_val_size 16 --num_epochs=35 --lr=1e-4 --dump_sample_results --render_every 25 --max_benchmark_batches=-1 --cls_bl 3 --cls_latent_size 256 --cls_dropout=0.3 --cls_depth 3
