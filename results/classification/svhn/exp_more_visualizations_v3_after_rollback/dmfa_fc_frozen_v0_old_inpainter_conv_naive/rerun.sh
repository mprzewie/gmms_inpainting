# 2021-03-16 19:19:27.432872
python train_classifier.py --experiment_name=exp_more_visualizations_v3_after_rollback/dmfa_fc_frozen_v0_old_inpainter_conv_naive --inpainter_type=dmfa --inpainter_path ../results/inpainting/svhn/fullconv/dmfa_mse_10_eps --dataset svhn --img_size 32 --mask_hidden_h 16 --mask_hidden_w 16 --num_epochs=10 --lr=1e-3 --dump_sample_results --render_every 3 --dataset_root /mnt/remote/wmii_gmum_projects/datasets/vision/SVHN/ --convar_type naive
